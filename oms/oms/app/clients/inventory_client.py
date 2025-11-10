import grpc
from oms.app.clients import inventory_pb2, inventory_pb2_grpc

INVENTORY_ADDR = "inventory-service:50051"


def check_availability(items: dict[str, int]) -> dict[str, bool]:
    """
    Check the availability of items in the inventory.

    Args:
        items (dict[str, int]): A dictionary where keys are item IDs and values are the required quantities.

    Returns:
        dict[str, bool]: A dictionary where keys are item IDs and values indicate availability (True if available, False otherwise).
    """
    with grpc.insecure_channel(INVENTORY_ADDR) as channel:
        stub = inventory_pb2_grpc.InventoryServiceStub(channel)
        request = inventory_pb2.InventoryRequest(items=items)
        response = stub.CheckAvailability(request)
        return dict(response.availability)


def reserve_items(items: dict[str, int]) -> tuple[bool, dict[str, dict]]:
    """
    Reserve items in the inventory.

    Args:
        items (dict[str, int]): A dictionary where keys are item IDs and values are the quantities to reserve.

    Returns:
        tuple[bool, dict[str, dict]]: A tuple containing a boolean indicating overall success and a dictionary with reservation results for each item.
    """
    with grpc.insecure_channel(INVENTORY_ADDR) as channel:
        stub = inventory_pb2_grpc.InventoryServiceStub(channel)
        request = inventory_pb2.ReserveRequest(items=items)
        response = stub.ReserveItems(request)
        results = {key: {"success": value.success, "message": value.message}
                   for key, value in response.results.items()}
        return response.overallSuccess, results


def release_items(items: dict[str, int]) -> tuple[bool, dict[str, dict]]:
    """
    Release (undo) reserved items in the inventory.
    """
    with grpc.insecure_channel(INVENTORY_ADDR) as channel:
        stub = inventory_pb2_grpc.InventoryServiceStub(channel)
        request = inventory_pb2.ReleaseRequest(items=items)
        response = stub.ReleaseItems(request)
        return response.overallSuccess, response.messages
