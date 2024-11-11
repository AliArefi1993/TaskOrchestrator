from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks, Request
from app.tasks import asr_task, translation_task
import threading
import json
app = FastAPI()

current_transcription = None  # Shared variable to hold transcription result

@app.post("/process-audio/")
async def process_audio(file: UploadFile, background_tasks: BackgroundTasks):
    
    audio_data = await file.read()
    global current_transcription

    current_transcription = None
    # Send audio to ASR service via RabbitMQ
    asr_task.send_audio_to_asr(audio_data)
    
    # Define a callback to handle the translation once ASR is done
    def handle_translation_response(translated_text):
        global current_transcription
        current_transcription = json.loads(translated_text)

    # Start a background thread to listen for the translation response
    background_thread = threading.Thread(target=translation_task.retrieve_translation_response, args=(handle_translation_response,))
    background_thread.start()
    
    return {"status": "Processing started"}

@app.get("/result/")
async def get_result():
    global current_transcription
    if current_transcription is None:
        return {"status": "processing", "result": None}
    else:
        return {"status": "completed", "result": current_transcription}
