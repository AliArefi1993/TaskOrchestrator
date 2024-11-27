from faststream.rabbit import RabbitBroker, RabbitMessage
from faststream import FastStream
from config import RABBITMQ_HOST, RESPONSE_QUEUE
from models.transcription import TranscriptionDocument
import json, logging
from uuid import UUID

logger = logging.getLogger(__name__)

def queue_listener():
    broker = RabbitBroker(url=f"amqp://{RABBITMQ_HOST}")
    app = FastStream(broker)
    
    @broker.subscriber(RESPONSE_QUEUE)
    async def process_translation_request(message: RabbitMessage):
        try:
            logger.info('Receive new translation')
            message_data = message.body
            message_json = json.loads(message_data)
            text_to_translate = message_json.get("translated_text", "")
            chain = message_json.get("chain", "")
            request_id_str = message_json.get("request_id", "") 
            request_id = UUID(request_id_str)

            # Query a document
            transcription = await TranscriptionDocument.find_one({
                'status': 'processing', 
                'chain': chain,
                'request_id': request_id
            })
            # # Update a document
            transcription.status = "completed"
            transcription.result = text_to_translate
            await transcription.save()

        except Exception as e:
            logger.error(f"Error processing translation request: {e}")
    return app, broker
