from typing import Optional

MOCK_BEHAVIOR = {
    "force_fail": False,
    "force_captured": False,
    "threshold_decline": 0.0,   # z.B. 1000.0 -> Beträge >= 1000 abgelehnt
    "simulate_timeout": False,
}

class PaymentError(Exception):
    """
    Simulated transport/timeout error for payment operations.
    
    This exception is raised by the mock payment service to simulate
    network failures or timeouts that might occur in a real payment service.
    """

async def authorize(
    order_id: str,
    amount: float,
    currency: str = "EUR",
    method: str = "CARD",
    correlation_id: Optional[str] = None,
) -> dict:
    """
    Simulate payment authorization with configurable behavior.
    
    This mock function simulates the payment service's authorization process.
    Behavior can be controlled via the MOCK_BEHAVIOR dictionary:
    - force_fail: If True, payment always fails
    - force_captured: If True, payment status is "CAPTURED", otherwise "AUTHORIZED"
    - threshold_decline: Payments with amount >= threshold are declined
    - simulate_timeout: If True, raises PaymentError to simulate timeout
    
    Args:
        order_id: The unique identifier of the order being paid for
        amount: The payment amount as a float
        currency: The currency code (default: "EUR")
        method: The payment method (default: "CARD")
        correlation_id: Optional correlation ID for distributed tracing (not used in mock)
    
    Returns:
        dict: A dictionary containing payment information with keys:
            - id: Generated payment ID
            - orderId: The order ID
            - status: Payment status ("CAPTURED", "AUTHORIZED", or "FAILED")
            - message: Status message
    
    Raises:
        PaymentError: If simulate_timeout is True in MOCK_BEHAVIOR
    """
    # Timeout/Transport simulieren -> Exception wie echter Client
    if MOCK_BEHAVIOR["simulate_timeout"]:
        raise PaymentError("Payment timeout (mock)")

    # Geschäftsregeln simulieren
    if MOCK_BEHAVIOR["force_fail"]:
        return {"id": f"pay_{order_id}", "orderId": order_id, "status": "FAILED", "message": "forced fail (mock)"}

    threshold = MOCK_BEHAVIOR["threshold_decline"]
    if threshold and amount >= threshold:
        return {"id": f"pay_{order_id}", "orderId": order_id, "status": "FAILED", "message": f"declined >= {threshold} (mock)"}

    status = "CAPTURED" if MOCK_BEHAVIOR["force_captured"] else "AUTHORIZED"
    return {
        "id": f"pay_{order_id}",
        "orderId": order_id,
        "status": status,
        "message": f"{status.lower()} (mock)"
    }