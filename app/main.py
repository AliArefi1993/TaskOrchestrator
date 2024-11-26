import asyncio
import uvicorn
import uuid
from typing import Optional
from fastapi import FastAPI, UploadFile, Query, status, File
from tasks import asr_task
from tasks.translation_task import queue_listener
from config_db import init_db
from models.transcription import TranscriptionDocument
from helpers.translation_result import get_concatenated_transcription_results


faststream_app, broker = queue_listener()

# FastAPI Initialization
fastapi_app = FastAPI()

@fastapi_app.on_event("startup")
async def on_startup():
    await init_db()
    await TranscriptionDocument.delete_all()    

@fastapi_app.post("/process-audio/", status_code=status.HTTP_202_ACCEPTED)
async def process_audio(file: UploadFile = File(...)):
    request_id = uuid.uuid4()
    audio_data = await file.read()

    chunk_files = await asr_task.chunck_audio_file_base_on_silence(audio_data)
    for i, chunk in enumerate(chunk_files):
        await asr_task.send_audio_to_asr(request_id, chunk, i, broker)
        transcription = TranscriptionDocument(status="processing", chain=i, request_id=request_id)
        await transcription.insert()

    print(f'{i+1} number of chunks created and ready to ASR.')

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
