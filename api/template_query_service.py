import io
import os
import json
import asyncio
from PIL import Image
from bson import ObjectId
from pydantic import BaseModel
from api.database_config import db
from typing import Optional, List, Tuple, Union
from image_generator.image_generator import QueryFull
from api.image_generator_config import image_generator
from motor.motor_asyncio import AsyncIOMotorGridFSBucket


template_queries_collection = db["template_queries"]
templates_jsons_directory = "templates/jsons"
templates_images_directory = "templates/images"


class TemplateQueryFull(BaseModel):
    query_full: QueryFull
    image_id: Optional[str] = None


class TemplateQueryIdModel(BaseModel):
    template_query_id: str


async def init_template_queries_collection():
    await template_queries_collection.drop()
    template_num = 1
    for filename in os.listdir(templates_jsons_directory):
        if filename.endswith(".json"):
            full_path = os.path.join(templates_jsons_directory, filename)
            with open(full_path, "r", encoding="utf-8") as f:
                template_query = json.load(f)
                query_full = QueryFull(**template_query["query_full"])
                image_full_path = None
                if template_query["image_path"]:
                    image_full_path = os.path.join(templates_images_directory, template_query["image_path"])
                if os.path.exists(image_full_path):
                    image = Image.open(image_full_path)
                else:
                    image, _ = image_generator.generate_image_query_full(query_full)
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                buf.seek(0)
                image_bytes = buf.read()
                fs_bucket = AsyncIOMotorGridFSBucket(db)
                grid_out = fs_bucket.open_upload_stream("image.png")
                await grid_out.write(image_bytes)
                await grid_out.close()
                template_query_full = TemplateQueryFull(query_full=query_full, image_id=str(grid_out._id))
                template_query_full_dict = template_query_full.model_dump()
                template_query_full_dict["_id"] = str(template_num)
                template_num += 1
                await template_queries_collection.insert_one(template_query_full_dict)


async def get_image_bytes(image_id: str) -> bytes:
    fs_bucket = AsyncIOMotorGridFSBucket(db)
    grid_in = await fs_bucket.open_download_stream(ObjectId(image_id))
    image_bytes = await grid_in.read()
    grid_in.close()
    return image_bytes


async def get_query_document(template_query_id: str) -> TemplateQueryFull:
    template_query = await template_queries_collection.find_one({"_id": template_query_id})
    template_query = TemplateQueryFull(**template_query)
    if not template_query:
        raise ValueError("Query not found")
    return template_query


async def retrieve_query_and_image(query_id: str) -> Tuple[QueryFull, bytes]:
    stored_query = await get_query_document(query_id)
    query_full = stored_query.query_full
    if stored_query.image_id:
        image_bytes = await get_image_bytes(stored_query.image_id)
    else:
        loop = asyncio.get_running_loop()
        image, _ = await loop.run_in_executor(None, image_generator.generate_image_query_full, query_full)
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)
        image_bytes = buf.read()
    return query_full, image_bytes


async def retrieve_all_queries_and_images(full_metadata: Optional[bool] = True) -> List[Tuple[Union[QueryFull, TemplateQueryIdModel], bytes]]:
    template_queries = await template_queries_collection.find({}).to_list(length=None)
    if full_metadata:
        queries_image_bytes = [(QueryFull(**template_query["query_full"]),
                                await get_image_bytes(template_query["image_id"]))
                               for template_query in template_queries]
    else:
        queries_image_bytes = [(TemplateQueryIdModel(template_query_id=str(template_query["_id"])),
                                await get_image_bytes(template_query["image_id"]))
                               for template_query in template_queries]
    return queries_image_bytes
