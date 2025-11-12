import json
import sys
import time

import pika
from wms_service.publisher import publish_message

from wms_service.rabbitmq.message_sender import send_log_message

EXCHANGE_NAME = "wms_event"


def callback(ch, method, properties, body):
    """
    Process incoming order messages from RabbitMQ.
    
    This callback function handles order processing workflow:
    1. Receives order data from the OMS
    2. Simulates picking items (with 5 second delay)
    3. Simulates packing order (with 5 second delay)
    4. Simulates shipping order
    5. Publishes status updates back to OMS at each stage
    
    Args:
        ch: The RabbitMQ channel object
        method: Method frame containing delivery information
        properties: Message properties
        body: The message body containing JSON-encoded order data
    """
    data = json.loads(body)
    print(f"data: {data}")
    send_log_message("wms", "order_received", f"Received order: {data.get('order')}")
    order_id = json.loads(data.get("order")).get("orderId")
    print("order id :" + order_id)
    publish_message(order_id, "items_picked", f"{order_id}: Picked the ordered items")
    send_log_message("wms", "items_picked", f"Picked items for order {order_id}")
    time.sleep(5)
    publish_message(order_id, "order_packed", f"{order_id}: Packed the complete order. Ready for shipping")
    send_log_message("wms", "order_packed", f"Packed order {order_id}")
    time.sleep(5)
    publish_message(order_id, "order_shipped", f"{order_id}: Order was shipped.")
    send_log_message("wms", "order_shipped", f"Shipped order {order_id}")


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
            send_log_message("wms", "connection_attempt", f"Attempt {attempt} to connect to RabbitMQ")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
            print("Verbindung zu RabbitMQ erfolgreich!")
            send_log_message("wms", "connection_success", "Successfully connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ noch nicht erreichbar, warte {delay} Sekunden...")
            send_log_message("wms", "connection_failed", f"Attempt {attempt} failed to connect to RabbitMQ")
            time.sleep(delay)
    print("Konnte keine Verbindung zu RabbitMQ herstellen. Beende Service.")
    send_log_message("wms", "connection_failed_final", "Failed to connect to RabbitMQ after multiple attempts")
    sys.exit(1)


def main():
    """
    Start the Warehouse Management Service and wait for order messages.
    
    This function:
    1. Establishes connection to RabbitMQ
    2. Sets up the exchange and queue for receiving orders
    3. Starts consuming messages and processing orders
    4. Handles graceful shutdown on keyboard interrupt
    
    """
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    # Exchange deklarieren
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic")

    # Queue für Logs deklarieren
    result = channel.queue_declare(queue="warehouse_queue", durable=True)
    queue_name = result.method.queue

    # Queue mit Exchange verbinden
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key="order.wms")

    print("Warehouse-Service läuft und wartet auf Nachrichten ")
    send_log_message("wms", "service_started", "Warehouse service started and waiting for messages")
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Warehouse-Service beendet.")
        send_log_message("wms", "service_stopped", "Warehouse service stopped by user")
        connection.close()


if __name__ == "__main__":
    main()
