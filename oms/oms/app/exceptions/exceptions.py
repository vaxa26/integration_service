class BaseError(Exception):
    """
    Base class for all application-specific errors with message support.
    
    This class provides a common base for all custom exceptions in the OMS,
    ensuring consistent error handling and message formatting.
    """

    def __init__(self, message):
        """
        Initialize the base error with a message.
        
        Args:
            message: The error message describing what went wrong
        """
        self.message = message
        super().__init__(message)


class PaymentDeclinedError(BaseError):
    """
    Exception raised when a payment authorization is declined.
    
    This typically occurs when the customer's account has insufficient funds
    or the payment method is invalid.
    """
    pass


class CustomerNotFoundError(BaseError):
    """
    Exception raised when a customer ID cannot be found in the payment service.
    
    This occurs when attempting to process a payment for a non-existent customer.
    """
    pass


class ReserveError(BaseError):
    """
    Exception raised when item reservation fails in the inventory service.
    
    This occurs when items cannot be reserved even though they appeared available
    during the availability check (e.g., due to race conditions or concurrent orders).
    """
    pass


class InventoryUnavailableError(BaseError):
    """
    Exception raised when requested items are not available in the inventory.
    
    This occurs during the availability check phase when one or more items
    do not have sufficient stock to fulfill the order.
    """
    pass
