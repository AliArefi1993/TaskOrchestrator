from faststream.rabbit import RabbitBroker, RabbitMessage
from faststream import FastStream
from config import RABBITMQ_HOST, RESPONSE_QUEUE
from models.transcription import TranscriptionDocument
import json

def queue_listener():
    broker = RabbitBroker(url=f"amqp://{RABBITMQ_HOST}")
    app = FastStream(broker)
    
    @broker.subscriber(RESPONSE_QUEUE)
    async def process_translation_request(message: RabbitMessage):
        try:
            message_data = message.body
            message_json = json.loads(message_data)
            text_to_translate = message_json.get("translated_text", "")
            chain = message_json.get("chain", "")

            # Query a document
            transcription = await TranscriptionDocument.find_one({'status':'processing', 'chain':chain})

            # # Update a document
            transcription.status = "completed"
            transcription.result = text_to_translate
            await transcription.save()

        except Exception as e:
            print(f"Error processing translation request: {e}")
    return app, broker
