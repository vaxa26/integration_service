from typing import Dict, Tuple

# --- Verhalten steuerbar ---
OUT_OF_STOCK: set[str] = set()
RESERVE_FAIL: set[str] = set()
INFINITE_STOCK: bool = True

def check_availability(items: Dict[str, int]) -> Dict[str, bool]:
    """
    Simuliert Lagerverfügbarkeit.
    - Wenn INFINITE_STOCK True: alles verfügbar außer in OUT_OF_STOCK.
    - Sonst: einfache Regel -> Menge <= 5 ist verfügbar, außer OUT_OF_STOCK.
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
    Simuliert Reservierung.
    - Produkte in RESERVE_FAIL schlagen fehl.
    - Wenn Verfügbarkeit vorher okay, ist Reservierung i. d. R. erfolgreich.
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