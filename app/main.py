from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from app.tasks import asr_task, translation_task
import threading

app = FastAPI()

current_transcription = None  # Shared variable to hold transcription result

@app.post("/process-audio/")
async def process_audio(file: UploadFile, background_tasks: BackgroundTasks):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
    
    audio_data = await file.read()
    
    # Send audio to ASR service via RabbitMQ
    asr_task.send_audio_to_asr(audio_data)
    
    # Define a callback to handle the translation once ASR is done
    def handle_translation_response(translated_text):
        global current_transcription
        current_transcription = translated_text

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
