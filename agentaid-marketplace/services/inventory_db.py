# services/inventory_db.py
import sqlite3
from contextlib import contextmanager
from typing import Dict, Any, List, Tuple

def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def tx(conn: sqlite3.Connection):
    try:
        conn.execute("BEGIN IMMEDIATE;")
        yield
        conn.execute("COMMIT;")
    except Exception:
        conn.execute("ROLLBACK;")
        raise

def ensure_supplier(conn: sqlite3.Connection, name: str, lat: float, lon: float, label: str,
                    base_lead_h: float, radius_km: float, delivery_mode: str) -> int:
    row = conn.execute("SELECT id FROM suppliers WHERE name = ?", (name,)).fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO suppliers(name, lat, lon, label, base_lead_h, radius_km, delivery_mode) VALUES (?,?,?,?,?,?,?)",
        (name, lat, lon, label, base_lead_h, radius_km, delivery_mode),
    )
    return cur.lastrowid

def upsert_item(conn: sqlite3.Connection, supplier_id: int, name: str, qty: int,
                unit: str | None, unit_price: float | None):
    conn.execute("""
        INSERT INTO items(supplier_id, name, unit, unit_price, qty)
        VALUES (?,?,?,?,?)
        ON CONFLICT(supplier_id, name) DO UPDATE SET
          unit=COALESCE(excluded.unit, items.unit),
          unit_price=COALESCE(excluded.unit_price, items.unit_price),
          qty=items.qty + excluded.qty
    """, (supplier_id, name.lower(), unit, unit_price or 0.0, qty))

def get_supplier_config(conn: sqlite3.Connection, name: str) -> Dict[str, Any] | None:
    s = conn.execute("SELECT * FROM suppliers WHERE name=?", (name,)).fetchone()
    if not s:
        return None
    return dict(s)

def get_inventory(conn: sqlite3.Connection, supplier_id: int) -> List[Dict[str, Any]]:
    rows = conn.execute("SELECT name, unit, unit_price, qty FROM items WHERE supplier_id=?", (supplier_id,)).fetchall()
    return [dict(r) for r in rows]

def offer_for_request(conn: sqlite3.Connection, supplier_id: int, requested: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], float]:
    inv = {r["name"]: r for r in get_inventory(conn, supplier_id)}
    offered, ratios = [], []
    for r in requested:
        want = int(r.get("qty", 0))
        name = r["name"].lower()
        stock = inv.get(name, {"qty": 0, "unit": None, "unit_price": 0.0})
        offer = min(want, int(stock["qty"]))
        if want > 0:
            ratios.append(min(offer / float(want), 1.0))
        offered.append({
            "name": r["name"],
            "qty": offer,
            "unit": stock.get("unit"),
            "unit_price": float(stock.get("unit_price", 0.0))
        })
    cov = sum(ratios) / len(ratios) if ratios else 0.0
    return offered, cov

def add_inventory_item(conn: sqlite3.Connection, supplier_id: int, name: str, qty: int, 
                      unit: str, unit_price: float, category: str = "general"):
    """Add inventory item for a supplier"""
    conn.execute("""
        INSERT INTO items(supplier_id, name, qty, unit, unit_price, category)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(supplier_id, name) DO UPDATE SET
          qty = qty + excluded.qty,
          unit = COALESCE(excluded.unit, items.unit),
          unit_price = COALESCE(excluded.unit_price, items.unit_price),
          category = COALESCE(excluded.category, items.category)
    """, (supplier_id, name.lower(), qty, unit, unit_price, category))

def deduct_allocation(conn: sqlite3.Connection, supplier_id: int, items: List[Dict[str, Any]]):
    with tx(conn):
        for it in items:
            name = it["name"].lower()
            qty  = int(it.get("qty", 0))
            # lock row and update
            row = conn.execute("SELECT qty FROM items WHERE supplier_id=? AND name=?",
                               (supplier_id, name)).fetchone()
            if not row:
                continue
            new_qty = max(0, int(row["qty"]) - qty)
            conn.execute("UPDATE items SET qty=? WHERE supplier_id=? AND name=?",
                         (new_qty, supplier_id, name))
