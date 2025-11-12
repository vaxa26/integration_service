from fastapi import APIRouter, HTTPException, status, Request

from ..exceptions.exceptions import PaymentDeclinedError, ReserveError, CustomerNotFoundError, InventoryUnavailableError
from ..schema.schema import createOrder, Order, OrderStatus
from ..service import oms_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(payload: createOrder, request: Request):
    """
    Create a new order in the system.
    
    This endpoint handles the complete order creation process including:
    - Idempotency checks
    - Amount validation
    - Inventory availability checks
    - Item reservation
    - Payment authorization
    
    Args:
        payload: The order creation request containing customer, items, and shipping details
        request: FastAPI request object used to extract correlation ID for distributed tracing
    
    Returns:
        Order: The created order object with status "PROCESSED"
    
    Raises:
        HTTPException: 400 if order ID already exists or amount validation fails
        HTTPException: 402 if payment is declined
        HTTPException: 404 if customer is not found
        HTTPException: 409 if inventory is unavailable or reservation fails
    """
    try:
        return await oms_service.create_order(payload, correlation_id=getattr(request.state, "correlation_id", None))
    except PaymentDeclinedError as e:
        raise HTTPException(status_code=402, detail=str(e))
    except ReserveError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InventoryUnavailableError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except oms_service.DuplicateOrderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{orderId}", response_model=Order)
def get_order(orderId: str):
    """
    Retrieve a specific order by its ID.
    
    Args:
        orderId: The unique identifier of the order to retrieve
    
    Returns:
        Order: The order object if found
    
    Raises:
        HTTPException: 404 if the order is not found
    """
    order = oms_service.get_order(orderId)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.get("/", response_model=list[Order])
def list_orders():
    """
    Retrieve all orders in the system.
    
    Returns:
        list[Order]: A list of all orders currently stored in the system
    """
    return oms_service.list_orders()


@router.get("/{orderId}/status", response_model=OrderStatus)
def get_order_status(orderId: str):
    """
    Get the current status of a specific order.
    
    Args:
        orderId: The unique identifier of the order
    
    Returns:
        OrderStatus: An object containing the order ID and its current status
    
    Raises:
        HTTPException: 404 if the order is not found
    """
    order = oms_service.get_order(orderId)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderStatus(orderId=order.orderId, status=order.status)
