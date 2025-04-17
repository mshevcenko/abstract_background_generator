import os
import json
from PIL import Image
from pydantic import BaseModel
from api.configs.database_config import db
from typing import Optional, List, Tuple
from image_generator.image_generator import QueryFull
from api.services.store_query_service import StoredQueryFullInfo
from api.services import store_query_service, image_service, image_generation_service


TEMPLATE_PRIORITY = 10


stored_queries_collection = db["stored_queries"]
templates_jsons_directory = "templates/jsons"
templates_images_directory = "templates/images"


class TemplateQueryFull(BaseModel):
    query_full: QueryFull
    image_id: Optional[str] = None


class TemplateQueryIdModel(BaseModel):
    template_query_id: str


async def init_template_queries_collection():
    for filename in os.listdir(templates_jsons_directory):
        if filename.endswith(".json"):
            full_path = os.path.join(templates_jsons_directory, filename)
            template_name = filename.removesuffix(".json")
            with open(full_path, "r", encoding="utf-8") as f:
                template_query = json.load(f)
                query_full = QueryFull(**template_query)
                image_full_path = os.path.join(templates_images_directory, template_name + ".png")
                image = None
                if os.path.exists(image_full_path):
                    image = Image.open(image_full_path)
                await store_query_service.store_query_full(query_full, image=image, is_template=True)


async def retrieve_template_and_image_bytes(query_id: str) -> Tuple[StoredQueryFullInfo, bytes]:
    stored_query_full_info, image_bytes = await store_query_service.retrieve_query_full_info_and_image_bytes(query_id)
    return stored_query_full_info, image_bytes


async def retrieve_all_templates_and_images_bytes() -> List[Tuple[StoredQueryFullInfo, bytes, str]]:
    template_queries = await stored_queries_collection.find({"is_template": True}).to_list(length=None)
    queries_image_bytes = [(StoredQueryFullInfo(**template_query), await image_service.retrieve_image_bytes(template_query["image_id"]), str(template_query["_id"])) for template_query in template_queries]
    return queries_image_bytes
