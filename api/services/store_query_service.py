import asyncio
from PIL import Image
from typing import Optional, Tuple

from bson import ObjectId
from pydantic import BaseModel
from api.configs.database_config import db
from image_generator.image_generator import QueryFull
from api.services import image_service, image_generation_service

BASE_PRIORITY = 5
TEMPLATE_PRIORITY = 10


stored_queries_collection = db["stored_queries"]


class StoredQueryFullInfo(BaseModel):
    query_full: QueryFull
    likes_count: int = 0
    is_template: bool = False
    image_id: Optional[str] = None
    query_id: Optional[str] = None


async def store_query_full(query_full: QueryFull,
                           image: Optional[Image] = None,
                           is_template: bool = False) -> str:
    stored_query = await stored_queries_collection.find_one({"query_full": query_full.model_dump()})
    if stored_query is None:
        stored_query_full = StoredQueryFullInfo(query_full=query_full, is_template=is_template)
        stored_query = await stored_queries_collection.insert_one(stored_query_full.model_dump())
        query_id = str(stored_query.inserted_id)
        if image is None:
            asyncio.create_task(image_generation_service.generate_image_and_save(query_full,
                                                                                 query_id,
                                                                                 stored_queries_collection))
        else:
            await image_generation_service.save_image(image, query_id, stored_queries_collection)
    else:
        query_id = str(stored_query["_id"])
        if not stored_query["image_id"] and image is None:
            asyncio.create_task(image_generation_service.generate_image_and_save(query_full, query_id, stored_queries_collection))
        elif not stored_query["image_id"]:
            await image_generation_service.save_image(image, query_id, stored_queries_collection)
    return query_id


async def retrieve_query_full_info(query_id: str) -> StoredQueryFullInfo:
    stored_query = await stored_queries_collection.find_one({"_id": ObjectId(query_id)})
    return StoredQueryFullInfo(**stored_query)


async def retrieve_query_full_info_and_image_bytes(query_id: str) -> Tuple[StoredQueryFullInfo, Image]:
    stored_query = await retrieve_query_full_info(query_id)
    if not stored_query.image_id:
        image, _ = await image_generation_service.generate_image(stored_query.query_full)
        image_bytes = image_service.image_to_bytes(image)
        asyncio.create_task(image_generation_service.generate_image_and_save(stored_query.query_full, query_id, stored_queries_collection))
    else:
        image_bytes = await image_service.retrieve_image_bytes(stored_query.image_id)
    return stored_query, image_bytes


async def retrieve_query_full_info_and_image(query_id: str) -> Tuple[StoredQueryFullInfo, Image]:
    stored_query = await retrieve_query_full_info(query_id)
    if not stored_query.image_id:
        image = await image_generation_service.generate_image(stored_query.query_full)
        asyncio.create_task(image_generation_service.generate_image_and_save(stored_query.query_full, query_id, stored_queries_collection))
    else:
        image = await image_service.retrieve_image(stored_query.image_id)
    return stored_query, image