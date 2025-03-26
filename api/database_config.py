import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
client.get_io_loop = asyncio.get_running_loop
db = client["abstract_image_generator_db"]