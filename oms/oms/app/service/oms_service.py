from oms.app.clients import inventory_client
from oms.app.schema.schema import createOrder, Order

_STORE: dict[str, Order] = {}
order_items = {"P-3344": 1, "P-8821": 2}


def list_orders() -> list[Order]:
    return list(_STORE.values())


def get_order(orderId: str) -> Order | None:
    return _STORE.get(orderId)


def create_order(payload: createOrder) -> Order:
    if payload.orderId in _STORE:
        raise ValueError("Order with this ID already exists")

    total = sum(i.price * i.quantity for i in payload.items)
    if total != payload.totalAmount:
        raise ValueError("Total amount does not match sum of item prices")

    order = Order(**payload.model_dump(), status="Pending")
    _STORE[payload.orderId] = order

    availability = inventory_client.check_availability(order_items)
    print("Availability:", availability)

    overall_success, reservation_results = inventory_client.reserve_items(order_items)
    print("Overall Success:", overall_success)


    return order


# Example usage of inventory client
