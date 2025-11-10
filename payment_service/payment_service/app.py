from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime, timezone
from payment_service.mock_data import mock_accounts

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

    print("Starting payment")

    # Konto suchen
    account = next((a for a in mock_accounts if a["customer_id"] == request.customer_id), None)
    if not account:
        raise HTTPException(status_code=404, detail="Customer account not found.")

    # Guthaben prüfen
    if request.amount > account["balance"]:
        raise HTTPException(status_code=402, detail="Payment declined: account not covered.")

    # Zahlung erfolgreich -> Guthaben abbuchen
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

    print(f"[LOG] Payment created for {request.customer_id}: {payment}")
    return payment