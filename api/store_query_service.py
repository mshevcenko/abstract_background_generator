import io
import asyncio
from typing import Tuple
from bson import ObjectId
from pydantic import BaseModel
from api.database_config import db
from image_generator.image_generator import QueryFull
from api.image_generator_config import image_generator
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

stored_queries_collection = db["stored_queries"]

class StoredQueryFull(BaseModel):
    query_full: QueryFull
    image_id: str = None

class QueryIdModel(BaseModel):
    query_id: str


async def generate_and_save_image(query_id: str, query_full: QueryFull):
    loop = asyncio.get_running_loop()
    image, _ = await loop.run_in_executor(None, image_generator.generate_image_query_full, query_full)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    image_bytes = buf.read()
    fs_bucket = AsyncIOMotorGridFSBucket(db)
    grid_out = fs_bucket.open_upload_stream("image.png")
    await grid_out.write(image_bytes)
    await grid_out.close()
    await stored_queries_collection.update_one(
        {"_id": ObjectId(query_id)},
        {"$set": {"image_id": str(grid_out._id)}}
    )

async def store_query_full(query_full: QueryFull) -> QueryIdModel:
    stored_query_full = StoredQueryFull(query_full=query_full)
    result = await stored_queries_collection.insert_one(stored_query_full.model_dump())
    query_id = str(result.inserted_id)
    asyncio.create_task(generate_and_save_image(query_id, query_full))
    return QueryIdModel(query_id=query_id)


async def get_query_document(query_id: str) -> StoredQueryFull:
    stored_query = await stored_queries_collection.find_one({"_id": ObjectId(query_id)})
    stored_query = StoredQueryFull(**stored_query)
    if not stored_query:
        raise ValueError("Query not found")
    return stored_query


async def get_image_bytes(image_id: str) -> bytes:
    fs_bucket = AsyncIOMotorGridFSBucket(db)
    grid_in = await fs_bucket.open_download_stream(ObjectId(image_id))
    image_bytes = await grid_in.read()
    grid_in.close()
    return image_bytes


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