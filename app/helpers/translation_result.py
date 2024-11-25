
from models.transcription import TranscriptionDocument

async def get_concatenated_transcription_results() -> str:
    transcriptions_cursor = await TranscriptionDocument.find().sort("chain").to_list()
    concatenated_result = " ".join([t.result for t in transcriptions_cursor if t.result])

    return concatenated_result