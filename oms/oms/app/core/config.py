import os

USE_MOCKS = os.getenv("USE_MOCKS", "true").lower() == "true" 
PAYMENT_URL = os.getenv("PAYMENT_URL", "http://localhost:8001")
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://localhost:8002")
RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@localhost:5672/")
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "EUR")
LOG_FILE = os.getenv("LOG_FILE", "oms.log")
