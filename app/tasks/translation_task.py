import pika
from app.config import RABBITMQ_HOST, TRANSLATION_QUEUE, TRANSLATION_RESULT

def send_text_to_translation(asr_text):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    
    channel.queue_declare(queue=TRANSLATION_QUEUE)
    
    channel.basic_publish(
        exchange="",
        routing_key=TRANSLATION_QUEUE,
        body=asr_text
    )
    
    connection.close()

def retrieve_translation_response(callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    
    channel.queue_declare(queue=TRANSLATION_RESULT)
    
    def on_message(ch, method, properties, body):
        callback(body.decode())
    
    channel.basic_consume(queue=TRANSLATION_RESULT, on_message_callback=on_message, auto_ack=True)
    channel.start_consuming()
