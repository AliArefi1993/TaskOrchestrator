import asyncio
import uvicorn
import uuid
from typing import Optional
from fastapi import FastAPI, UploadFile, Query, status, File, BackgroundTasks
from tasks import asr_task
from tasks.translation_task import queue_listener
from config_db import init_db
from models.transcription import TranscriptionDocument
from helpers.translation_result import get_concatenated_transcription_results
from config import ENABLE_CHUNK_AUDIO
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

faststream_app, broker = queue_listener()

# FastAPI Initialization
fastapi_app = FastAPI()

@fastapi_app.on_event("startup")
async def on_startup():
    await init_db()
    await TranscriptionDocument.delete_all()    

@fastapi_app.post("/process-audio/", status_code=status.HTTP_202_ACCEPTED)
async def process_audio(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    request_id = uuid.uuid4()
    audio_data = await file.read()
    background_tasks.add_task(asr_task.handel_asr, audio_data, request_id, broker)
    logger.info(f'request id is: {request_id}')
    return {"status": "Processing started", "request_id": request_id}

@fastapi_app.get("/result/")
async def get_result(request_id: Optional[str] = Query(None)):
    if not request_id:
        return {"status": "error", "message": "request_id is required"}
    request_id = uuid.UUID(request_id)
    transcription = await TranscriptionDocument.find_one({'request_id':request_id})
    processing_transcription = await TranscriptionDocument.find_one({'status':'processing', 'request_id':request_id})
    
    if transcription is None:
        return {"status": "not_found", "result": None}
    elif processing_transcription:
        return {"status": "processing", "result": None}
    concatenated_result = await get_concatenated_transcription_results(request_id)
    return {
        "status": 'completed',
        "result": concatenated_result
    }


async def start_services():
    """Run FastStream and FastAPI together."""
    faststream_task = asyncio.create_task(faststream_app.run())

    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    fastapi_task = asyncio.create_task(server.serve())

    await asyncio.gather(faststream_task, fastapi_task)

if __name__ == "__main__":
    asyncio.run(start_services())
