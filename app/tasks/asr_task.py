from config import ENABLE_CHUNK_AUDIO, ASR_QUEUE
from pydub import AudioSegment
from pydub.silence import split_on_silence
import io, json

async def send_audio_to_asr(audio_data: bytes, chain: int, broker):
    broker.connect()
    binary_data = audio_data.read()
    message = json.dumps({"audio_data": binary_data.decode('latin1'), "chain": chain})  # Ensure binary data is encoded
    await broker.publish(
        message=message,
        routing_key=ASR_QUEUE
    )

async def chunck_audio_file_base_on_silence(audio_file, silence_thresh=-40, min_silence_len=1000):
    audio = AudioSegment.from_file(io.BytesIO(audio_file))
    if ENABLE_CHUNK_AUDIO:
        chunks = split_on_silence(audio, silence_thresh=silence_thresh, min_silence_len=min_silence_len)  # Adjust thresholds as needed
    else:
        chunks=[audio]
    chunk_files = []
    for chunk in chunks:
        buffer = io.BytesIO()
        chunk.export(buffer, format="wav")
        buffer.seek(0)
        chunk_files.append(buffer)
    return chunk_files
