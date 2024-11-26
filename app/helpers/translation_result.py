
from models.transcription import TranscriptionDocument

async def get_concatenated_transcription_results(request_id: str) -> str:
    transcriptions_cursor = await TranscriptionDocument.find({"request_id": request_id}).sort("chain").to_list()
    concatenated_result = " ".join([t.result for t in transcriptions_cursor if t.result])

    return concatenated_result