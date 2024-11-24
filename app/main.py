import asyncio
import uvicorn
from fastapi import FastAPI, UploadFile, BackgroundTasks, status
from tasks import asr_task
from tasks.translation_task import queue_listener


faststream_app, broker = queue_listener()
current_transcription = None  # Shared variable to hold transcription result

# FastAPI Initialization
fastapi_app = FastAPI()

@fastapi_app.post("/process-audio/", status_code=status.HTTP_202_ACCEPTED)
async def process_audio(file: UploadFile, background_tasks: BackgroundTasks):
    audio_data = await file.read()
    global current_transcription

    current_transcription = None
    # Send audio to ASR service via RabbitMQ
    broker.connect()
    await asr_task.send_audio_to_asr(audio_data, broker)
    
    return {"status": "Processing started"}

@fastapi_app.get("/result/")
async def get_result():
    global current_transcription
    if current_transcription is None:
        return {"status": "processing", "result": None}
    else:
        return {"status": "completed", "result": current_transcription}


async def start_services():
    """Run FastStream and FastAPI together."""
    faststream_task = asyncio.create_task(faststream_app.run())

    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    fastapi_task = asyncio.create_task(server.serve())

    await asyncio.gather(faststream_task, fastapi_task)

if __name__ == "__main__":
    asyncio.run(start_services())
