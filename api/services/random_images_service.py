import asyncio
from bson import ObjectId
from pydantic import BaseModel
from api.services import image_service
from typing import Optional, Tuple, List
from api.configs.database_config import db
from api.configs.image_generator_config import image_generator
from image_generator.image_generator import QueryFull, ImageMetadataFull
from api.configs.process_executor_config import process_executor as random_process_executor


POOL_SIZE = 50
DEFAULT_RANDOM_WIDTH = 640
DEFAULT_RANDOM_HEIGHT = 480
DEFAULT_MIN_LAYERS_COUNT = 2
DEFAULT_MAX_LAYERS_COUNT = 5
TIMEOUT = 12
TIMEOUT_BETWEEN = 3


random_queries_collection = db["random_queries"]
queue = asyncio.Queue(maxsize=POOL_SIZE*2)


class RandomQueryModel(BaseModel):
    query_full: QueryFull
    image_id: Optional[str] = None
    is_checked: bool = False


async def store_random_image(query_id_to_remove: Optional[str] = None):
    loop = asyncio.get_running_loop()
    success = False
    while not success:
        query_full = image_generator.random_query(DEFAULT_RANDOM_WIDTH,
                                                  DEFAULT_RANDOM_HEIGHT,
                                                  DEFAULT_MIN_LAYERS_COUNT,
                                                  DEFAULT_MAX_LAYERS_COUNT)
        try:
            image, _ = await loop.run_in_executor(
                random_process_executor,
                image_generator.generate_image_query_full,
                query_full
            )
            image_id = await image_service.store_image(image)
            random_query = RandomQueryModel(query_full=query_full, image_id=image_id)
            await random_queries_collection.insert_one(random_query.model_dump())
            success = True
            del image
        except Exception:
            pass
    if query_id_to_remove:
        await random_queries_collection.delete_one({"_id": ObjectId(query_id_to_remove)})


async def store_random_images(count: int, query_ids_to_remove: Optional[List[str]] = None):
    for i in range(count):
        if query_ids_to_remove is not None:
            await store_random_image(query_ids_to_remove[i])
        else:
            await store_random_image()


async def create_random_queries_worker():
    while True:
        item = await queue.get()
        if item is not None:
            count, ids = item
            await store_random_images(count, ids)
        queue.task_done()


async def init_random_queries():
    current_size = await random_queries_collection.count_documents({})
    await random_queries_collection.update_many(
        {},
        {"$set": {"is_checked": False}}
    )
    if current_size > POOL_SIZE:
        cursor = random_queries_collection.aggregate([{"$sample": {"size": current_size - POOL_SIZE}}])
        ids_to_delete = [doc["_id"] async for doc in cursor]
        if ids_to_delete:
            await random_queries_collection.delete_many({"_id": {"$in": ids_to_delete}})
    asyncio.create_task(create_random_queries_worker())
    for _ in range(POOL_SIZE - current_size):
        queue.put_nowait((1, None))


async def retrieve_random_images_bytes(count: int) -> List[Tuple[ImageMetadataFull, bytes]]:
    if count > POOL_SIZE:
        count = POOL_SIZE
    current_size = await random_queries_collection.count_documents({})
    while current_size < count:
        await asyncio.sleep(1)
        current_size = await random_queries_collection.count_documents({})
    documents = await random_queries_collection.find({"is_checked": False}).limit(count).to_list(None)
    if len(documents) < 5:
        documents = await random_queries_collection.aggregate([{"$sample": {"size": count}}]).to_list(None)
    documents_ids_strs = [str(document["_id"]) for document in documents]
    documents_ids = [document["_id"] for document in documents]
    await random_queries_collection.update_many(
        {"_id": {"$in": documents_ids}},
        {"$set": {"is_checked": True}}
    )
    metadatas_images_bytes = []
    for document in documents:
        metadata = ImageMetadataFull(seed=None, **document["query_full"])
        image_bytes = await image_service.retrieve_image_bytes(document["image_id"])
        metadatas_images_bytes.append((metadata, image_bytes))
    for i in range(len(documents)):
        if not queue.full():
            queue.put_nowait((1, [documents_ids_strs[i]]))
    return metadatas_images_bytes