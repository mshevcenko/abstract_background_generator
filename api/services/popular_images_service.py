from PIL import Image
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument
from typing import Optional, Tuple, List
from api.configs.database_config import db
from image_generator.image_generator import QueryFull
from api.services import store_query_service, image_service
from api.services.store_query_service import StoredQueryFullInfo


stored_queries_collection = db["stored_queries"]


async def like_query_id(query_id: str) -> Optional[StoredQueryFullInfo]:
    updated_query = await stored_queries_collection.find_one_and_update(
        {"_id": ObjectId(query_id)},
        {"$inc": {"likes_count": 1}},
        return_document=ReturnDocument.AFTER,
        upsert=False
    )
    if updated_query is None:
        return None
    stored_query_full_info = StoredQueryFullInfo(**updated_query)
    stored_query_full_info.query_id = query_id
    return stored_query_full_info


async def like_query_full(query_full: QueryFull) -> Optional[StoredQueryFullInfo]:
    stored_query = await stored_queries_collection.find_one({"query_full": query_full.model_dump()})
    if stored_query is None:
        query_id = await store_query_service.store_query_full(query_full)
    else:
        query_id = str(stored_query["_id"])
    return await like_query_id(query_id)


async def dislike_query_id(query_id: str) -> Optional[StoredQueryFullInfo]:
    updated_query = await stored_queries_collection.find_one_and_update(
        {"_id": ObjectId(query_id)},
        [
            {
                "$set": {
                    "likes_count": {
                        "$max": [
                            {"$subtract": ["$likes_count", 1]},
                            0
                        ]
                    }
                }
            }
        ],
        return_document=ReturnDocument.AFTER,
        upsert=False
    )
    stored_query_full_info = StoredQueryFullInfo(**updated_query)
    stored_query_full_info.query_id = query_id
    return stored_query_full_info


async def dislike_query_full(query_full: QueryFull) -> Optional[StoredQueryFullInfo]:
    stored_query = await stored_queries_collection.find_one({"query_full": query_full.model_dump()})
    if stored_query is None:
        query_id = await store_query_service.store_query_full(query_full)
    else:
        query_id = str(stored_query["_id"])
    return await dislike_query_id(query_id)


async def get_total() -> int:
    return await stored_queries_collection.count_documents({})


async def get_popular_images(page: Optional[int] = None,
                             page_size: Optional[int] = None) -> List[Tuple[bytes, StoredQueryFullInfo]]:
    cursor = stored_queries_collection.find({}).sort("likes_count", -1)
    if page_size is not None and page is not None:
        if page < 1:
            page = 1
        skip = (page - 1) * page_size
        documents = await cursor.skip(skip).limit(page_size).to_list(length=page_size)
    else:
        documents = await cursor.to_list(length=page_size)
    if not documents:
        return []
    images_metadatas = []
    for doc in documents:
        metadata = StoredQueryFullInfo(**doc)
        metadata.query_id = str(doc["_id"])
        image_bytes = await image_service.retrieve_image_bytes(metadata.image_id)
        images_metadatas.append((image_bytes, metadata))
    return images_metadatas


async def get_popular_image_by_id(query_id: str) -> Optional[Tuple[bytes, StoredQueryFullInfo]]:
    try:
        object_id = ObjectId(query_id)
    except Exception:
        return None
    doc = await stored_queries_collection.find_one({"_id": object_id})
    if not doc:
        return None
    metadata = StoredQueryFullInfo(**doc)
    metadata.query_id = str(doc["_id"])
    image_bytes = await image_service.retrieve_image_bytes(metadata.image_id)
    return image_bytes, metadata


async def get_popular_images_by_ids(query_ids: List[str]) -> List[Tuple[bytes, StoredQueryFullInfo]]:
    object_ids = [ObjectId(query_id) for query_id in query_ids]
    documents = await stored_queries_collection.find({"_id": {"$in": object_ids}}).to_list(length=None)
    if not documents:
        return []
    images_metadatas = []
    for doc in documents:
        metadata = StoredQueryFullInfo(**doc)
        metadata.query_id = str(doc["_id"])
        image_bytes = await image_service.retrieve_image_bytes(metadata.image_id)
        images_metadatas.append((image_bytes, metadata))
    return images_metadatas
