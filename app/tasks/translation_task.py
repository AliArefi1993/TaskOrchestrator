from faststream.rabbit import RabbitBroker
from config import RABBITMQ_HOST, TRANSLATION_QUEUE, TRANSLATION_RESULT

broker = RabbitBroker(f"amqp://guest:guest@{RABBITMQ_HOST}/")

async def send_text_to_translation(asr_text: str):
    await broker.publish(
        message=asr_text,
        routing_key=TRANSLATION_QUEUE
    )

async def retrieve_translation_response(callback):
    @broker.subscriber(TRANSLATION_RESULT)
    async def on_message(message: str):
        await callback(message)
