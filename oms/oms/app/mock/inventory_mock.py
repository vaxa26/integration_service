from typing import Dict, Tuple

# --- Verhalten steuerbar ---
OUT_OF_STOCK: set[str] = set()
RESERVE_FAIL: set[str] = set()
INFINITE_STOCK: bool = True

def check_availability(items: Dict[str, int]) -> Dict[str, bool]:
    """
    Simulate inventory availability checking.
    
    This mock function simulates the inventory service's availability check.
    Behavior can be controlled via module-level flags:
    - If INFINITE_STOCK is True: all items are available except those in OUT_OF_STOCK set
    - If INFINITE_STOCK is False: items with quantity <= 5 are available, except those in OUT_OF_STOCK set
    
    Args:
        items: A dictionary where keys are product IDs and values are requested quantities
    
    Returns:
        Dict[str, bool]: A dictionary mapping product IDs to availability status (True if available, False otherwise)
    """
    result: Dict[str, bool] = {}
    for pid, qty in items.items():
        if pid in OUT_OF_STOCK:
            result[pid] = False
        elif INFINITE_STOCK:
            result[pid] = True
        else:
            result[pid] = qty <= 5
    return result

def reserve_items(items: Dict[str, int]) -> Tuple[bool, Dict[str, Dict[str, object]]]:
    """
    Simulate item reservation in the inventory.
    
    This mock function simulates the inventory service's reservation process.
    Behavior can be controlled via module-level flags:
    - Products in RESERVE_FAIL set will always fail reservation
    - Products in OUT_OF_STOCK set will fail reservation
    - Other products will succeed if availability was previously confirmed
    
    Args:
        items: A dictionary where keys are product IDs and values are quantities to reserve
    
    Returns:
        Tuple[bool, Dict[str, Dict[str, object]]]: A tuple containing:
            - A boolean indicating overall success (True if all items reserved successfully)
            - A dictionary mapping product IDs to reservation results with 'success' and 'message' keys
    """
    results: Dict[str, Dict[str, object]] = {}
    overall = True
    for pid, qty in items.items():
        if pid in RESERVE_FAIL:
            results[pid] = {"success": False, "message": "reservation failed (mock rule)"}
            overall = False
        elif pid in OUT_OF_STOCK:
            results[pid] = {"success": False, "message": "out of stock (mock rule)"}
            overall = False
        else:
            results[pid] = {"success": True, "message": f"reserved {qty} (mock)"}
    return overall, results