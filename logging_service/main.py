import datetime
import json
import pika
import time
import sys

EXCHANGE_NAME = "event_log"


def callback(ch, method, properties, body):
    """Wird aufgerufen, wenn eine Nachricht empfangen wird."""
    data = json.loads(body)
    timestamp = datetime.datetime.now()
    log_entry = f"[{timestamp}] {json.dumps(data)}\n"

    print(f"Received log: {log_entry.strip()}")

    with open("central_log.txt", "a") as f:
        f.write(log_entry)


def connect_to_rabbitmq(max_retries=10, delay=5):
    """Versucht, wiederholt eine Verbindung zu RabbitMQ aufzubauen."""
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
    """Startet den Logging-Service und wartet auf Nachrichten."""
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
