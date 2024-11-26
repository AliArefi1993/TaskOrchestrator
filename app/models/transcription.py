from pydantic import BaseModel
from beanie import Document
from typing import Optional
from uuid import UUID

class Transcription(BaseModel):
    request_id: UUID
    status: str
    result: Optional[str] = None
    chain: int

    class Settings:
        collection = "transcriptions"  # MongoDB collection name


class TranscriptionDocument(Transcription, Document):
    pass
