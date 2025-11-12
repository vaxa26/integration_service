import asyncio
import json

import aio_pika
import traceback
from oms.app.service.oms_service import write_in_store
RABBITMQ_URL = "amqp://guest:guest@rabbitmq/"
RETRY_DELAY = 5



async def start_wms_listener():
    """
    Start an asynchronous RabbitMQ listener for WMS events.
    
    This function continuously listens for messages from the WMS service on the
    'oms_event' exchange. It includes retry logic to handle connection failures
    and will automatically reconnect if the connection is lost.
    
    The listener processes order status updates from the warehouse management system
    and updates the order status in the OMS store accordingly.
    """
    print("[OMS] start_wms_listener() wurde aufgerufen.")
    while True:
        print("[OMS] Starte neue Verbindungsrunde...")
        try:
            print("[OMS] Versuche Verbindung zu RabbitMQ...")
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            print("[OMS] Verbindung zu RabbitMQ erfolgreich!")

            channel = await connection.channel()
            exchange = await channel.declare_exchange("oms_event", aio_pika.ExchangeType.TOPIC)
            queue = await channel.declare_queue("oms_queue", durable=True)
            await queue.bind(exchange, routing_key="oms")

            async def callback(message: aio_pika.IncomingMessage):
                """
                Async callback function to process incoming RabbitMQ messages from WMS.
                
                Args:
                    message: The incoming message object containing order event data
                """
                async with message.process():
                    print("[OMS] Nachricht vom WMS erhalten:", message.body.decode())
                    write_in_store("1234", message)

            await queue.consume(callback)
            print("[OMS] Listener aktiv. Warte auf Nachrichten...")

            await asyncio.Future()  # bleibt blockiert, bis Verbindung stirbt

        except Exception as e:
            print("[OMS] Fehler im try-Block:")
            traceback.print_exc()
            print(f"[OMS] Neuer Versuch in {RETRY_DELAY} Sekunden...")
            await asyncio.sleep(RETRY_DELAY)
