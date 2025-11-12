import grpc

from server import inventory_pb2, inventory_pb2_grpc


def test_check_availability():
    """
    Test the CheckAvailability gRPC method of the inventory service.
    
    This function creates a test request with sample product IDs and quantities,
    calls the CheckAvailability method, and prints the response showing which
    items are available.
    """
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = inventory_pb2_grpc.InventoryServiceStub(channel)

        request = inventory_pb2.InventoryRequest(items={
            "ORD-2025-11-4-1752": 2,
            "ORD-2025-11-4-1755": 1
        })

        response = stub.CheckAvailability(request)
        print("CheckAvailability Response:")
        print(response.availability)


def test_reserve_items():
    """
    Test the ReserveItems gRPC method of the inventory service.
    
    This function creates a test request with sample product IDs and quantities,
    calls the ReserveItems method, and prints the response showing reservation
    results for each item.
    """
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = inventory_pb2_grpc.InventoryServiceStub(channel)

        request = inventory_pb2.ReserveRequest(items={
            "ORD-2025-11-4-1752": 2,
            "ORD-2025-11-4-1755": 1
        })

        response = stub.ReserveItems(request)
        print("ReserveItems Response:")
        print(response)


if __name__ == "__main__":
    test_check_availability()
    print("-----------")
    test_reserve_items()
