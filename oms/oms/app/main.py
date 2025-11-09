from fastapi import FastAPI
from .routers.orders import router as orders


app = FastAPI(
    title = "OMS API",
    description = "Order Management System API",
    version = "1.0.0"
)

app.include_router(orders, prefix="/orders", tags=["Orders"])