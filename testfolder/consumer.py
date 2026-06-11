import os
import pika

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
channel.queue_declare(queue='detection_jobs', durable=True)

def callback(ch, method, properties, body):
    print(f"[x] Received: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='detection_jobs', on_message_callback=callback)

print('[*] Waiting for messages. CTRL+C to stop.')
channel.start_consuming()