from decimal import Decimal
from typing import Optional

from oms.app.clients import inventory_client as inventory
from oms.app.clients import payment_client as payment
from oms.app.schema.schema import createOrder, Order
from oms.app.rabbitmq.message_sender import send_log_message, send_wms_message
from oms.app.exceptions.exceptions import PaymentDeclinedError, ReserveError, InventoryUnavailableError, \
    CustomerNotFoundError

_STORE: dict[str, Order] = {}
ALLOWED_RESTOCK_PID = "ORD-2025-11-4-1755"

def write_in_store(order_id, status):
    _STORE[order_id].status = status

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
    missing = {pid: qty for pid, qty in items_map.items() if not availability.get(pid, False)}

    print("Checking availability du bastat")
    if missing:
        send_log_message("oms", "CreateOrder", f"{order_id}: missing -> {list(missing.keys())}, restocking…")

        # Restock NUR für das erlaubte Produkt und NUR wenn bestellte Menge == 0
        do_restock = (
            ALLOWED_RESTOCK_PID in missing
            and items_map.get(ALLOWED_RESTOCK_PID, None) == 0
        )

        if do_restock:
            try:
                overall, restock_results = inventory.restock_items({ALLOWED_RESTOCK_PID: missing[ALLOWED_RESTOCK_PID]})
                send_log_message("oms", "CreateOrder", f"{order_id}: restock_results={restock_results}")
            except Exception as e:
                send_log_message("oms", "CreateOrder", f"{order_id}: restock RPC failed: {e}")
                order = Order(**payload.model_dump(), status="BACKORDERED")
                _STORE[order_id] = order
                return order

            # Re-Check nach Restock
            availability = inventory.check_availability(items_map)
            still_missing = [pid for pid, ok in availability.items() if not ok]
            if still_missing:
                order = Order(**payload.model_dump(), status="BACKORDERED")
                _STORE[order_id] = order
                send_log_message("oms", "CreateOrder",
                                f"{order_id}: still missing after restock -> BACKORDERED {still_missing}")
                return order
            else:
                send_log_message("oms", "CreateOrder", f"{order_id}: restock successful -> continue")
        else:
            # Nicht unser Sonderfall -> wie gehabt BACKORDERED
            order = Order(**payload.model_dump(), status="BACKORDERED")
            _STORE[order_id] = order
            send_log_message("oms", "CreateOrder",
                            f"{order_id}: restock not allowed (needs {ALLOWED_RESTOCK_PID} with qty 0) -> BACKORDERED")
            return order
        
    # if not all(availability.values()): 
    #     send_log_message("oms", f"CreateOrder", f"{order_id}: Not every item available")
    #     raise InventoryUnavailableError(f"Availability check for order {payload.orderId} failed.")

    print("Items available. Starting reservation...")
    # 4) INVENTORY: reservieren
    reserved_ok, _results = inventory.reserve_items(items_map)
    if not reserved_ok:
        send_log_message("oms", f"CreateOrder", f"{order_id}: Couldn't reserve items")
        order = Order(**payload.model_dump(), status="CANCELLED")
        _STORE[order_id] = order
        send_log_message("oms", "CreateOrder", f"{order_id}: reserve failed -> CANCELLED {_results}")
        return order

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
    send_log_message("oms", "CreateOrder", f"{order_id}: Created payment {pay}")

    if pay.get("status") == "DECLINED":
        send_log_message("oms", "CreateOrder", f"{order_id}: payment declined")
        inventory.release_items(items_map)
        raise PaymentDeclinedError(f"Payment for customer with id {payload.customer.customerId} was declined.")

    if pay.get("status") == "NOTFOUND":
        send_log_message("oms", "CreateOrder", f"{order_id}: payment not found")
        inventory.release_items(items_map)
        raise CustomerNotFoundError(f"Customer with id {payload.customer.customerId} was not found.")

    # 6) Erfolg: Order abschließen
    send_log_message("oms", "CreateOrder", f"{order_id}: payment successfully")

    order = Order(**payload.model_dump(), status="PROCESSED")
    _STORE[order_id] = order
    send_wms_message(payload.json())
    return order
