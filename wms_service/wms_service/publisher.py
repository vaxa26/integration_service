import json

import pika


# https://www.rabbitmq.com/tutorials/tutorial-one-python
def publish_message(order_id: str, event: str, message: str):
    """Sendet item_picked-Nachricht an RabbitMQ."""

    event_to_routing_key = {"items_picked": "item.picked",
                            "order_packed": "order.packed",
                            "order_shipped": "order.shipped"}

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
        channel = connection.channel()

        channel.exchange_declare(exchange='oms_event', exchange_type='topic')
        payload = {
            "orderId": order_id,
            "event": event,
            "message": message
        }

        # https://medium.com/@sujakhu.umesh/rabbitmq-with-python-from-basics-to-advanced-messaging-patterns-a-practical-guide-18f8b43b94f8
        # Working with JSON Messages in RabbitMQ
        channel.basic_publish(
            exchange='oms_event',
            routing_key='oms',
            body=json.dumps(payload)
        )
        print(f" [x] Sent {payload}")
        connection.close()

    except Exception as e:
        print(f" [!] Failed to send message: {e}")
