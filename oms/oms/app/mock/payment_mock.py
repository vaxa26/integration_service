from typing import Optional

MOCK_BEHAVIOR = {
    "force_fail": False,
    "force_captured": False,
    "threshold_decline": 0.0,   # z.B. 1000.0 -> Beträge >= 1000 abgelehnt
    "simulate_timeout": False,
}

class PaymentError(Exception):
    """Simulierter Transport-/Timeoutfehler."""

async def authorize(
    order_id: str,
    amount: float,
    currency: str = "EUR",
    method: str = "CARD",
    correlation_id: Optional[str] = None,
) -> dict:
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