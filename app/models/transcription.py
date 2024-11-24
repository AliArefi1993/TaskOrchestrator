from pydantic import BaseModel
from beanie import Document
from typing import Optional

class Transcription(BaseModel):
    status: str
    result: Optional[str] = None

    class Settings:
        collection = "transcriptions"  # MongoDB collection name


class TranscriptionDocument(Transcription, Document):
    pass
