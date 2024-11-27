from config import ENABLE_CHUNK_AUDIO, ASR_QUEUE
from pydub import AudioSegment
from pydub.silence import split_on_silence
import io, json, logging
from uuid import UUID
from models.transcription import TranscriptionDocument

logger = logging.getLogger(__name__)  # Use the same logger instance

async def handel_asr(audio_data, request_id, broker):
    if ENABLE_CHUNK_AUDIO:
        chunk_files = await chunck_audio_file_base_on_silence(audio_data)
    else:
        chunk_files = [audio_data]
    
    for i, chunk in enumerate(chunk_files):
        await send_audio_to_asr(request_id, chunk, i, broker)
        transcription = TranscriptionDocument(status="processing", chain=i, request_id=request_id)
        await transcription.insert()
    logger.info(f'{i+1} number of chunks created and ready to ASR.')
    
async def send_audio_to_asr(request_id: UUID, audio_data: bytes, chain: int, broker):
    message = json.dumps({
        "audio_data": audio_data.decode('latin1'),
        "chain": chain,
        "request_id": str(request_id)
})
    await broker.publish(
        message=message,
        routing_key=ASR_QUEUE
    )

async def chunck_audio_file_base_on_silence(audio_file, silence_thresh=-40, min_silence_len=700):
    audio = AudioSegment.from_file(io.BytesIO(audio_file))
    chunks = split_on_silence(audio, silence_thresh=silence_thresh, min_silence_len=min_silence_len)  # Adjust thresholds as needed
    chunk_files = []
    for chunk in chunks:
        buffer = io.BytesIO()
        chunk.export(buffer, format="wav")
        buffer.seek(0)
        binary_data = buffer.read()
        chunk_files.append(binary_data)
    return chunk_files
