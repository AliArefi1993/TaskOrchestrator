import asyncio
import uvicorn
from fastapi import FastAPI, UploadFile, BackgroundTasks, status
from tasks import asr_task
from tasks.translation_task import queue_listener
from config_db import init_db
from models.transcription import TranscriptionDocument


faststream_app, broker = queue_listener()

# FastAPI Initialization
fastapi_app = FastAPI()

@fastapi_app.on_event("startup")
async def on_startup():
    await init_db()
    await TranscriptionDocument.delete_all()    

@fastapi_app.post("/process-audio/", status_code=status.HTTP_202_ACCEPTED)
async def process_audio(file: UploadFile):
    audio_data = await file.read()

    await TranscriptionDocument.delete_all()    

    # Send audio to ASR service via RabbitMQ
    broker.connect()
    await asr_task.send_audio_to_asr(audio_data, broker)

    # Create a new transcription document in MongoDB
    transcription = TranscriptionDocument(status="processing")
    await transcription.insert()

    return {"status": "Processing started"}

@fastapi_app.get("/result/")
async def get_result():
    # Fetch the transcription document from MongoDB by its ID
    transcription = await TranscriptionDocument.find_one({})
    
    if transcription is None:
        return {"status": "not_found", "result": None}
    
    return {
        "status": transcription.status,
        "result": transcription.result
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
