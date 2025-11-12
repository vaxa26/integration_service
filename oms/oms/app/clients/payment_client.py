import httpx
from typing import Optional
from oms.app.core.config import PAYMENT_URL, REQUEST_TIMEOUT


class PaymentError(Exception):
    """
    Custom exception raised when payment service operations fail.
    
    This exception is used to wrap various payment service errors including
    network errors, timeouts, and invalid responses.
    """


async def authorize(
    order_id: str,
    customer_id: str,
    amount: float,
    method: str = "CARD",
    correlation_id: Optional[str] = None
) -> dict:
    """
    Authorize a payment with the payment service.
    
    This method sends a payment authorization request to the payment service
    and handles various response scenarios including declined payments and
    customer not found errors.
    
    Args:
        order_id: The unique identifier of the order being paid for
        customer_id: The unique identifier of the customer making the payment
        amount: The payment amount as a float
        method: The payment method (default: "CARD")
        correlation_id: Optional correlation ID for distributed tracing
    
    Returns:
        dict: A dictionary containing payment information including:
            - payment_id: The unique payment identifier
            - status: Payment status ("CAPTURED", "AUTHORIZED", "DECLINED", "NOTFOUND")
            - Additional fields may be present depending on the response
    
    Raises:
        PaymentError: If the payment service request fails or returns an invalid response
    """
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
        if e.response.status_code == 402:
            return {"status": "DECLINED"}
        if e.response.status_code == 404:
            return {"status": "NOTFOUND"}
    except httpx.HTTPError as e:
        raise PaymentError(f"Payment service HTTP error: {e}") from e
