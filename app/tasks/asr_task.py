from config import RABBITMQ_HOST, ASR_QUEUE

async def send_audio_to_asr(audio_data: bytes, broker):
    broker.connect()
    await broker.publish(
        message=audio_data,
        routing_key=ASR_QUEUE
    )
