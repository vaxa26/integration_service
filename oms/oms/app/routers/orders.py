from fastapi import APIRouter, HTTPException, status

from ..schema.schema import createOrder, Order
from ..service import oms_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(payload: createOrder):
    order = oms_service.create_order(payload)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.get("/{orderId}", response_model=Order)
def get_order(orderId: str):
    order = oms_service.get_order(orderId)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.get("/", response_model=list[Order])
def list_orders():
    return oms_service.list_orders()
