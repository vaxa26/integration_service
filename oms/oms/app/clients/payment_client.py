import httpx
from typing import Optional
from oms.app.core.config import PAYMENT_URL, REQUEST_TIMEOUT


class PaymentError(Exception):
    """Custom exception for payment errors."""


async def authorize(
    order_id: str,
    customer_id: str,
    amount: float,
    method: str = "CARD",
    correlation_id: Optional[str] = None
) -> dict:
    headers = {}
    if correlation_id:
        headers["X-Correlation-ID"] = correlation_id

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                f"{PAYMENT_URL}/payments",
                json={
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "amount": amount,
                    "method": method
                },
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

            if not {"payment_id", "status"}.issubset(data):
                raise PaymentError("Invalid response from payment service")

            return data

    except httpx.RequestError as e:
        raise PaymentError(f"Payment service request error: {e}") from e
    except httpx.HTTPStatusError as e:
        raise PaymentError(f"Payment service returned error status: {e.response.status_code}") from e
    except httpx.HTTPError as e:
        raise PaymentError(f"Payment service HTTP error: {e}") from e
