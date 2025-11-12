import datetime
import json
import pika
import time
import sys

EXCHANGE_NAME = "event_log"


def callback(ch, method, properties, body):
    """
    Process incoming log messages from RabbitMQ.
    
    This callback function receives log messages from all services,
    formats them with a timestamp, and writes them to the central log file.
    
    Args:
        ch: The RabbitMQ channel object
        method: Method frame containing delivery information
        properties: Message properties
        body: The message body containing JSON-encoded log data
    """
    data = json.loads(body)
    timestamp = datetime.datetime.now()
    log_entry = f"[{timestamp}] {json.dumps(data)}\n"

    print(f"Received log: {log_entry.strip()}")

    with open("central_log.txt", "a") as f:
        f.write(log_entry)


def connect_to_rabbitmq(max_retries=10, delay=5):
    """
    Attempt to establish a connection to RabbitMQ with retry logic.
    
    This function tries to connect to RabbitMQ multiple times with delays
    between attempts. This is useful when RabbitMQ is starting up or
    temporarily unavailable.
    
    Args:
        max_retries: Maximum number of connection attempts (default: 10)
        delay: Number of seconds to wait between retry attempts (default: 5)
    
    Returns:
        pika.BlockingConnection: A connection object if successful
    
    Raises:
        SystemExit: If all connection attempts fail
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Verbindungsversuch {attempt}/{max_retries} zu RabbitMQ...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
            print("Verbindung zu RabbitMQ erfolgreich!")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ noch nicht erreichbar, warte {delay} Sekunden...")
            time.sleep(delay)
    print("Konnte keine Verbindung zu RabbitMQ herstellen. Beende Service.")
    sys.exit(1)


def main():
    """
    Start the centralized logging service and wait for log messages.
    
    This function:
    1. Establishes connection to RabbitMQ
    2. Sets up the exchange and queue for receiving logs from all services
    3. Starts consuming messages and writing them to the central log file
    4. Handles graceful shutdown on keyboard interrupt
    """
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    # Exchange deklarieren
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic")

    # Queue für Logs deklarieren
    result = channel.queue_declare(queue="central_logging_queue", durable=True)
    queue_name = result.method.queue

    # Queue mit Exchange verbinden
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key="log.*")

    print("Logging-Service läuft und wartet auf Nachrichten (log.*)")
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Logging-Service beendet.")
        connection.close()


if __name__ == "__main__":
    main()
