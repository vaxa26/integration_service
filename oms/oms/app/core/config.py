import os

PAYMENT_URL = os.getenv("PAYMENT_URL", "http://payment-service:8080")
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://localhost:8002")
RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@localhost:5672/")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "EUR")
LOG_FILE = os.getenv("LOG_FILE", "oms.log")