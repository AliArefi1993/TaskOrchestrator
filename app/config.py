import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")

MONGODB_URI = os.getenv("MONGODB_URI","mongodb://root:password@mongodb:27017/mydatabase?authSource=admin")

ASR_QUEUE = "asr_task_queue"
TRANSLATION_QUEUE = "translation_task_queue"
RESPONSE_QUEUE = "response_queue"
TRANSLATION_RESULT = "translation_result"
ENABLE_CHUNK_AUDIO = True
