from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class Customer(BaseModel):
    customerId: str
    prename: str
    name: str


class OrderItem(BaseModel):
    productId: str
    quantity: int
    price: Decimal


class ShippingAddress(BaseModel):
    street: str
    city: str
    zipcode: str
    country: str


class createOrder(BaseModel):
    orderId: str
    customer: Customer
    items: List[OrderItem]
    totalAmount: Decimal
    ShippingAddress: ShippingAddress


class Order(createOrder):
    status: str = Field(default="Pending")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = None
