import os
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models.transcription import TranscriptionDocument
from config import MONGODB_URI


async def init_db():
    mongo_uri = os.getenv("MONGO_URI", MONGODB_URI)
    client = AsyncIOMotorClient(mongo_uri)
    await init_beanie(database=client.mydatabase, document_models=[TranscriptionDocument])
