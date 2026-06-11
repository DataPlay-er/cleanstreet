import os
import pika

# Connect to RabbitMQ
# Load credentials from environment variables
rabbitmq_user = os.getenv("RABBITMQ_USER", "rabbit")
rabbitmq_pass = os.getenv("RABBITMQ_PASS", "rabbit123")
rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    )
)

channel = connection.channel()

# Create a queue called 'detection_jobs'
channel.queue_declare(queue='detection_jobs', durable=True)

# Send a test message
message = '{"job_id": "001", "file": "video_001.mp4", "camera": "CAM_A1"}'
channel.basic_publish(
    exchange='',
    routing_key='detection_jobs',
    body=message,
    properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
)

print(f"[x] Sent: {message}")
connection.close()