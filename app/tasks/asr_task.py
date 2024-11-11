import pika
from app.config import RABBITMQ_HOST, ASR_QUEUE

def send_audio_to_asr(audio_data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    
    channel.queue_declare(queue=ASR_QUEUE)
    
    channel.basic_publish(
        exchange="",
        routing_key=ASR_QUEUE,
        body=audio_data
    )
    
    connection.close()
