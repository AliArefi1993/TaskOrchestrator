from fastapi import FastAPI, UploadFile, BackgroundTasks, status
from tasks import asr_task, translation_task
import threading
import json
from faststream.rabbit import RabbitBroker
import asyncio
from config import RABBITMQ_HOST, ASR_QUEUE, TRANSLATION_QUEUE
from faststream import FastStream
import uvicorn


broker = RabbitBroker(url=f"amqp://{RABBITMQ_HOST}")

# FastStream Initialization
app = FastStream(broker)

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
    
    # Define a callback to handle the translation once ASR is done
    def handle_translation_response(translated_text):
        global current_transcription
        current_transcription = json.loads(translated_text)

    # Start a background thread to listen for the translation response
    background_thread = threading.Thread(target=translation_task.retrieve_translation_response, args=(handle_translation_response,))
    background_thread.start()
    
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
    faststream_task = asyncio.create_task(app.run())

    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    fastapi_task = asyncio.create_task(server.serve())

    await asyncio.gather(faststream_task, fastapi_task)

if __name__ == "__main__":
    asyncio.run(start_services())
