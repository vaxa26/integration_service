from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from payment_service.mock_data import mock_accounts
from pydantic import BaseModel
from payment_service.rabbitmq.message_sender import send_log_message

app = FastAPI(title="Payment Service", version="1.0")


class PaymentRequest(BaseModel):
    order_id: str
    customer_id: str
    amount: float
    method: str


class PaymentResponse(BaseModel):
    payment_id: str
    order_id: str
    status: str
    amount: float
    created_at: str


@app.post("/payments", response_model=PaymentResponse, status_code=201)
def create_payment(request: PaymentRequest):
    """
    Create a new payment authorization.
    
    This endpoint processes payment requests by:
    1. Validating that the customer exists
    2. Checking if the account has sufficient balance
    3. Deducting the payment amount from the customer's balance
    4. Creating a payment record with status "CAPTURED"
    
    Args:
        request: The payment request containing order_id, customer_id, amount, and method
    
    Returns:
        PaymentResponse: The created payment object with payment_id, status, and timestamps
    
    Raises:
        HTTPException: 404 if the customer account is not found
        HTTPException: 402 if the payment is declined due to insufficient funds
    """
    print("Starting payment")
    send_log_message("payment", f"CreatePayment",
                     f"Starting payment for customer with id {request.customer_id}")

    account = next((a for a in mock_accounts if a["customer_id"] == request.customer_id), None)
    if not account:
        send_log_message("payment", f"CreatePayment",
                         f"No customer with id {request.customer_id} found. Returning with status code 404.")
        raise HTTPException(status_code=404, detail="Customer account not found.")

    # Guthaben prüfen
    if request.amount > account["balance"]:
        send_log_message("payment", f"CreatePayment",
                         f"Payment declined for customer {request.customer_id}. Account not covered.")
        raise HTTPException(status_code=402, detail="Payment declined: account not covered.")

    account["balance"] -= request.amount
    payment_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    payment = PaymentResponse(
        payment_id=payment_id,
        order_id=request.order_id,
        status="CAPTURED",
        amount=request.amount,
        created_at=created_at
    )
    send_log_message("payment", f"CreatePayment",
                     f"Created payment: {payment}")

    print(f"Payment created for {request.customer_id}: {payment}")
    return payment
