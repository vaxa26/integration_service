from decimal import Decimal
from typing import Optional

from oms.app.clients import inventory_client as inventory
from oms.app.clients import payment_client as payment
from oms.app.schema.schema import createOrder, Order

_STORE: dict[str, Order] = {}
order_items = {"P-3344": 1, "P-8821": 2}


def list_orders() -> list[Order]:
    return list(_STORE.values())


def get_order(orderId: str) -> Order | None:
    return _STORE.get(orderId)


class DuplicateOrderError(Exception):
    pass


async def create_order(payload: createOrder, correlation_id: Optional[str] = None) -> Order:
    # 1) Idempotenz: gleiche OrderId -> vorhandene Order zurückgeben
    if payload.orderId in _STORE:
        raise DuplicateOrderError("Order with this ID already exists")

    # 2) Betrag validieren (Decimal gegen Rundungsfehler)
    calc_total = sum(Decimal(i.price) * i.quantity for i in payload.items)
    if calc_total != Decimal(payload.totalAmount):
        raise ValueError("Total amount does not match sum of item prices")

    # 3) INVENTORY: Verfügbarkeit prüfen
    items_map = {i.productId: i.quantity for i in payload.items}
    availability = inventory.check_availability(items_map)
    #
    print("Checking availability")
    if not all(availability.values()):
        order = Order(**payload.model_dump(), status="CANCELLED")
        _STORE[payload.orderId] = order
        print("Not every item available")
        return order

    print("Items available. Starting reservation...")
    # 4) INVENTORY: reservieren
    reserved_ok, _results = inventory.reserve_items(items_map)
    if not reserved_ok:
        print("Couldn't reserve")
        order = Order(**payload.model_dump(), status="CANCELLED")
        _STORE[payload.orderId] = order
        return order

    print("Starting payment")

    # 5) PAYMENT: Zahlung autorisieren (REST)
    pay = await payment.authorize(
        order_id=payload.orderId,
        customer_id=payload.customer.customerId,
        amount=float(payload.totalAmount),
        method="CARD",
        correlation_id=correlation_id,
    )

    print(f"Crreated payment: {pay}")
    print(f"Status of pay: {pay.get('status')} ")

    # Kollegen-Service liefert z. B. status "AUTHORIZED"/"CAPTURED" oder "FAILED"
    if pay.get("status") not in {"AUTHORIZED", "CAPTURED"}:
        order = Order(**payload.model_dump(), status="CANCELLED")
        _STORE[payload.orderId] = order
        return order

    # 6) Erfolg: Order abschließen
    order = Order(**payload.model_dump(), status="PROCESSED")
    _STORE[payload.orderId] = order
    return order
