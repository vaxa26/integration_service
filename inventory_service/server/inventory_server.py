import json
import logging
import os
import sys
from concurrent import futures

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import grpc

from rabbitmq.message_sender import send_log_message
from . import inventory_pb2
from . import inventory_pb2_grpc

logger = logging.getLogger()

INVENTORY_DATA: dict = json.load(open("data/mock_data_inventory.json"))


class InventoryServiceServicer(inventory_pb2_grpc.InventoryServiceServicer):
    def CheckAvailability(self, request, context):
        """
        Function to check the availability of the requested items.
        :param request: The request containing a map with the ids and the quantity.
        :param context: Request context.
        :return: The map with the ids and a bool if the requested quantity is available.
        """
        availability: dict = {}
        items: dict = request.items
        logger.info(f"Checking availability for products with ids {items.keys()}")

        for product_id, quantity in items.items():
            send_log_message("inventory", "CheckAvailability",
                             f"Check availability for product {product_id}, Requested item count: {quantity}")
            available_items: int = INVENTORY_DATA.get(product_id, 0)
            if available_items >= quantity:
                availability[product_id] = True
                send_log_message("inventory", "CheckAvailability",
                                 f"Enough items available ({available_items})")

                continue
            availability[product_id] = False
            send_log_message("inventory", "CheckAvailability",
                             f"Not enough items available ({available_items})")

        return inventory_pb2.InventoryResponse(availability=availability)

    def ReserveItems(self, request, context):
        """
        Reserve items in the inventory.
        
        This gRPC method attempts to reserve the requested quantities of items.
        If successful, the quantities are deducted from available inventory.
        If any item cannot be reserved, the overall operation fails but partial
        reservations may have been made.
        
        Args:
            request: The gRPC request containing a map of product IDs to quantities
            context: gRPC request context
        
        Returns:
            ReserveResponse: A response containing overall success status and
                detailed results for each item including success status and messages
        """
        reserve_items: dict = request.items
        results: dict = {}
        overall_success: bool = True

        for product_id, quantity in reserve_items.items():
            logger.info(f"Reserving {quantity} pieces of the item {product_id}")
            available_quantity: int = INVENTORY_DATA.get(product_id, 0)

            if available_quantity >= quantity:
                INVENTORY_DATA[product_id] = available_quantity - quantity
                results[product_id] = inventory_pb2.ReserveStatus(
                    success=True,
                    message=f"Reserved {quantity} units"
                )
                send_log_message("inventory", "ReserveItems",
                                 f"Reserved {quantity} items of {product_id}")

                continue

            results[product_id] = inventory_pb2.ReserveStatus(
                success=False, message=f"Not enough items in the inventory."
            )
            send_log_message("inventory", "ReserveItems",
                             f"Couldn't reserve {quantity} items of {product_id}")

            overall_success = False

        return inventory_pb2.ReserveResponse(overallSuccess=overall_success, results=results)

    def ReleaseItems(self, request, context):
        """
        Release previously reserved items back to available inventory.
        
        This gRPC method is typically called when an order fails (e.g., payment declined)
        to return reserved items back to the available stock.
        
        Args:
            request: The gRPC request containing a map of product IDs to quantities to release
            context: gRPC request context
        
        Returns:
            ReleaseResponse: A response containing overall success status and
                messages for each released item
        """
        released_items = {}
        overall_success = True

        for product_id, quantity in request.items.items():
            available_quantity = INVENTORY_DATA.get(product_id, 0)
            INVENTORY_DATA[product_id] = available_quantity + quantity
            released_items[product_id] = f"Released {quantity} units"
            send_log_message("inventory", "ReleaseItems",
                             f"Released {quantity} items of {product_id}")

        return inventory_pb2.ReleaseResponse(
            overallSuccess=overall_success,
            messages=released_items
        )


def serve():
    """
    Start the gRPC inventory service server.
    
    This function initializes and starts the gRPC server on port 50051,
    making the inventory service available for client connections.
    The server runs until terminated.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    print("Inventory Service running on port 50051...")

    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
