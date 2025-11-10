from decimal import Decimal
from typing import Optional

from oms.app.clients import inventory_client as inventory
from oms.app.clients import payment_client as payment
from oms.app.schema.schema import createOrder, Order
from oms.app.rabbitmq.message_sender import send_log_message
from oms.app.exceptions.exceptions import PaymentDeclinedError, ReserveError, InventoryUnavailableError, \
    CustomerNotFoundError

_STORE: dict[str, Order] = {}
order_items = {"P-3344": 1, "P-8821": 2}


def list_orders() -> list[Order]:
    return list(_STORE.values())


def get_order(orderId: str) -> Order | None:
    return _STORE.get(orderId)


class DuplicateOrderError(Exception):
    pass


async def create_order(payload: createOrder, correlation_id: Optional[str] = None) -> Order:
    order_id = payload.orderId
    send_log_message("oms", f"CreateOrder",
                     f"{order_id}: Creating order")

    # 1) Idempotenz: gleiche OrderId -> vorhandene Order zurückgeben
    if order_id in _STORE:
        send_log_message("oms", f"CreateOrder",
                         f"{order_id}: Order already exists. Exiting...")
        raise DuplicateOrderError("Order with this ID already exists")

    # 2) Betrag validieren (Decimal gegen Rundungsfehler)
    calc_total = sum(Decimal(i.price) * i.quantity for i in payload.items)
    if calc_total != Decimal(payload.totalAmount):
        send_log_message("oms", f"CreateOrder",
                         f"{order_id}: Total amount does not match the sum of item prices")
        raise ValueError("Total amount does not match sum of item prices")

    # 3) INVENTORY: Verfügbarkeit prüfen
    items_map = {i.productId: i.quantity for i in payload.items}
    availability = inventory.check_availability(items_map)
  
    print("Checking availability")
    if not all(availability.values()): 
        send_log_message("oms", f"CreateOrder", f"{order_id}: Not every item available")
        raise InventoryUnavailableError(f"Availability check for order {payload.orderId} failed.")

    print("Items available. Starting reservation...")
    # 4) INVENTORY: reservieren
    reserved_ok, _results = inventory.reserve_items(items_map)
    if not reserved_ok:
        send_log_message("oms", f"CreateOrder", f"{order_id}: Couldn't reserve items")
        raise ReserveError(f"Reservation for order {order_id} failed")

    send_log_message("oms", f"CreateOrder", f"{order_id}: Starting payment")

    # 5) PAYMENT: Zahlung autorisieren (REST)
    pay = await payment.authorize(
        order_id=order_id,
        customer_id=payload.customer.customerId,
        amount=float(payload.totalAmount),
        method="CARD",
        correlation_id=correlation_id,
    )

    print(f"Created payment: {pay}")
    print(f"Status of pay: {pay.get('status')} ")
    send_log_message("oms", f"CreateOrder", f"{order_id}: Created payment {pay}")

    if pay.get("status") == "DECLINED":
        send_log_message("oms", f"CreateOrder", f"{order_id}: payment declined")
        inventory.release_items(items_map)
        raise PaymentDeclinedError(f"Payment for customer with id {payload.customer.customerId} was declined.")

    if pay.get("status") == "NOTFOUND":
        send_log_message("oms", f"CreateOrder", f"{order_id}: payment not found")
        inventory.release_items(items_map)
        raise CustomerNotFoundError(f"Customer with id {payload.customer.customerId} was not found.")

    # 6) Erfolg: Order abschließen
    send_log_message("oms", f"CreateOrder", f"{order_id}: payment successfully")

    order = Order(**payload.model_dump(), status="PROCESSED")
    _STORE[order_id] = order
    return order
