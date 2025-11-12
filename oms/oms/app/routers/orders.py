from fastapi import APIRouter, HTTPException, status, Request

from ..exceptions.exceptions import PaymentDeclinedError, ReserveError, CustomerNotFoundError, InventoryUnavailableError
from ..schema.schema import createOrder, Order, OrderStatus
from ..service import oms_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(payload: createOrder, request: Request):
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
    order = oms_service.get_order(orderId)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.get("/", response_model=list[Order])
def list_orders():
    return oms_service.list_orders()


@router.get("/{orderId}/status", response_model=OrderStatus)
def get_order_status(orderId: str):
    order = oms_service.get_order(orderId)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderStatus(orderId=order.orderId, status=order.status)
