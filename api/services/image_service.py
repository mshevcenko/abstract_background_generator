import io
from PIL import Image
from bson import ObjectId
from api.configs.database_config import db
from motor.motor_asyncio import AsyncIOMotorGridFSBucket


def image_to_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    image_bytes = buf.read()
    return image_bytes


async def store_image_bytes(image_bytes: bytes) -> str:
    fs_bucket = AsyncIOMotorGridFSBucket(db)
    grid_out = fs_bucket.open_upload_stream("image.png")
    await grid_out.write(image_bytes)
    await grid_out.close()
    return str(grid_out._id)


async def store_image(image: Image) -> str:
    image_bytes = image_to_bytes(image)
    return await store_image_bytes(image_bytes)


async def delete_image(image_id: str):
    fs_bucket = AsyncIOMotorGridFSBucket(db)
    await fs_bucket.delete(ObjectId(image_id))


async def retrieve_image_bytes(image_id: str) -> bytes:
    fs_bucket = AsyncIOMotorGridFSBucket(db)
    grid_in = await fs_bucket.open_download_stream(ObjectId(image_id))
    image_bytes = await grid_in.read()
    grid_in.close()
    return image_bytes


async def retrieve_image(image_id: str) -> Image:
    image_bytes = await retrieve_image_bytes(image_id)
    return Image.open(io.BytesIO(image_bytes))
