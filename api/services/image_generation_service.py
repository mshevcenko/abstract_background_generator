import asyncio
from PIL import Image
from bson import ObjectId
from typing import Tuple, Any
from api.services import image_service
from api.configs.image_generator_config import image_generator
from api.configs.process_executor_config import process_executor
from api.services.image_service import store_image, store_image_bytes
from image_generator.image_generator import QueryFull, ImageMetadataFull


async def generate_image(query_full: QueryFull) -> Tuple[Image, ImageMetadataFull]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_executor,
                                      image_generator.generate_image_query_full,
                                      query_full)


async def generate_image_bytes(query_full: QueryFull) -> Tuple[bytes, ImageMetadataFull]:
    image, metadata = await generate_image(query_full)
    return image_service.image_to_bytes(image), metadata


async def save_image(image: Image,
                     query_id: str,
                     collection: Any) -> None:
    image_id = await store_image(image)
    await collection.update_one(
        {"_id": ObjectId(query_id)},
        {"$set": {"image_id": image_id}}
    )


async def save_image_bytes(image_bytes: bytes,
                           query_id: str,
                           collection: Any) -> None:
    image_id = await store_image_bytes(image_bytes)
    await collection.update_one(
        {"_id": ObjectId(query_id)},
        {"$set": {"image_id": image_id}}
    )


async def generate_image_and_save(query_full: QueryFull,
                                  query_id: str,
                                  collection: Any) -> None:
    image, _ = await generate_image(query_full=query_full)
    image_id = await store_image(image)
    await collection.update_one(
        {"_id": ObjectId(query_id)},
        {"$set": {"image_id": image_id}}
    )