# agentaid-marketplace/services/inventory_db.py
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Iterable, Tuple

__all__ = [
    # Core API (current script relies on these)
    "connect",
    "ensure_supplier",
    "add_inventory_item",
    "get_supplier_config",
    "get_inventory",
    # Useful helpers
    "list_suppliers",
    "get_supplier_id_by_key",
    "get_supplier_by_key",
    "get_inventory_by_key",
    "upsert_inventory_item",
    "update_inventory_qty",
    "delete_inventory_item",
    "bulk_add_inventory_items",
    # Back-compat aliases (older projects may use these)
    "create_inventory_item",
    "add_item_to_inventory",
    "insert_inventory",
    "ensure_supplier_by_key",
    "get_db",
]

# ----------------------------
# Connection / Schema / Migrations
# ----------------------------

def connect(db_path: str) -> sqlite3.Connection:
    """
    Connects to SQLite, enables foreign keys, sets row_factory=Row,
    and ensures the schema (incl. migrations) is in place.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _pragma(conn)
    _ensure_schema(conn)
    _migrate(conn)  # run lightweight migrations if needed
    return conn

def _pragma(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("PRAGMA journal_mode = WAL;")   # better concurrency/resilience
    cur.execute("PRAGMA synchronous = NORMAL;") # good balance of safety/speed
    conn.commit()

def _ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # Suppliers table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        label TEXT NOT NULL,
        base_lead_h REAL NOT NULL,
        radius_km REAL NOT NULL,
        delivery_mode TEXT NOT NULL
    );
    """)

    # Inventory table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        qty INTEGER NOT NULL,
        unit TEXT NOT NULL,
        unit_price REAL NOT NULL,
        category TEXT NOT NULL,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    );
    """)

    # Track schema version for future migrations
    cur.execute("PRAGMA user_version;")
    ver = cur.fetchone()[0]
    if ver == 0:
        # Initial deployment
        cur.execute("PRAGMA user_version = 1;")

    conn.commit()

def _migrate(conn: sqlite3.Connection) -> None:
    """
    Lightweight migrations; safe to run repeatedly.
    - Adds a UNIQUE index on (supplier_id, name) to enable upserts.
    """
    cur = conn.cursor()

    # Create unique index if it doesn't exist
    cur.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory_supplier_name
    ON inventory (supplier_id, name);
    """)

    # Example future migration guard (increment user_version accordingly)
    cur.execute("PRAGMA user_version;")
    ver = cur.fetchone()[0]
    target = 2
    if ver < target:
        # Put future schema changes here.
        cur.execute("PRAGMA user_version = 2;")

    conn.commit()

@contextmanager
def transaction(conn: sqlite3.Connection):
    """
    Context manager for atomic operations.
    Usage:
        with transaction(conn):
            ...
    """
    try:
        yield
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()

# ----------------------------
# Suppliers
# ----------------------------

def ensure_supplier(conn: sqlite3.Connection,
                    key: str,
                    lat: float,
                    lon: float,
                    label: str,
                    base_lead_h: float,
                    radius_km: float,
                    delivery_mode: str) -> int:
    """
    Idempotently create or return a supplier by its unique `key`.
    Returns the supplier id.
    """
    cur = conn.cursor()
    cur.execute("SELECT id FROM suppliers WHERE key = ?;", (key,))
    row = cur.fetchone()
    if row:
        return int(row["id"])

    cur.execute("""
        INSERT INTO suppliers (key, lat, lon, label, base_lead_h, radius_km, delivery_mode)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (key, lat, lon, label, base_lead_h, radius_km, delivery_mode))
    conn.commit()
    return int(cur.lastrowid)

def get_supplier_id_by_key(conn: sqlite3.Connection, key: str) -> Optional[int]:
    cur = conn.cursor()
    cur.execute("SELECT id FROM suppliers WHERE key = ?;", (key,))
    row = cur.fetchone()
    return int(row["id"]) if row else None

def get_supplier_by_key(conn: sqlite3.Connection, key: str) -> Optional[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM suppliers WHERE key = ?;", (key,))
    row = cur.fetchone()
    return dict(row) if row else None

def list_suppliers(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("""
        SELECT id, key, label, lat, lon, base_lead_h, radius_km, delivery_mode
        FROM suppliers
        ORDER BY key;
    """)
    return [dict(r) for r in cur.fetchall()]

def get_supplier_config(conn: sqlite3.Connection, supplier_id: int) -> Dict[str, Any]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM suppliers WHERE id = ?;", (supplier_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Supplier id {supplier_id} not found")
    return dict(row)

# ----------------------------
# Inventory (Insert / Upsert / Query / Mutate)
# ----------------------------

def add_inventory_item(conn: sqlite3.Connection,
                       supplier_id: int,
                       name: str,
                       qty: int,
                       unit: str,
                       unit_price: float,
                       category: str) -> int:
    """
    Insert a single inventory item for a supplier. Returns the new inventory id.
    If an item with the same (supplier_id, name) already exists (due to the
    unique index), this will raise an IntegrityError. If you prefer automatic
    upsert/merge behavior, use `upsert_inventory_item`.
    """
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO inventory (supplier_id, name, qty, unit, unit_price, category)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (supplier_id, name, qty, unit, unit_price, category))
    conn.commit()
    return int(cur.lastrowid)

def upsert_inventory_item(conn: sqlite3.Connection,
                          supplier_id: int,
                          name: str,
                          qty: int,
                          unit: str,
                          unit_price: float,
                          category: str,
                          merge_qty: bool = True) -> int:
    """
    Insert or update an inventory item. If `merge_qty` is True, increments qty
    when the row already exists; otherwise it replaces the row's qty/unit/price/category.
    Returns the row id (new or existing).
    """
    cur = conn.cursor()
    if merge_qty:
        # ON CONFLICT … DO UPDATE: increment qty, and refresh unit/unit_price/category
        cur.execute("""
            INSERT INTO inventory (supplier_id, name, qty, unit, unit_price, category)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(supplier_id, name) DO UPDATE SET
                qty = inventory.qty + excluded.qty,
                unit = excluded.unit,
                unit_price = excluded.unit_price,
                category = excluded.category;
        """, (supplier_id, name, qty, unit, unit_price, category))
    else:
        # Replace all fields deterministically
        cur.execute("""
            INSERT INTO inventory (supplier_id, name, qty, unit, unit_price, category)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(supplier_id, name) DO UPDATE SET
                qty = excluded.qty,
                unit = excluded.unit,
                unit_price = excluded.unit_price,
                category = excluded.category;
        """, (supplier_id, name, qty, unit, unit_price, category))
    conn.commit()

    # Return id
    cur.execute("""
        SELECT id FROM inventory WHERE supplier_id = ? AND name = ?;
    """, (supplier_id, name))
    row = cur.fetchone()
    return int(row["id"])

def bulk_add_inventory_items(conn: sqlite3.Connection,
                             supplier_id: int,
                             items: Iterable[Dict[str, Any]],
                             upsert: bool = True,
                             merge_qty: bool = True) -> None:
    """
    Bulk insert/upsert inventory items (dicts with keys: name, qty, unit, unit_price, category).
    """
    with transaction(conn):
        for it in items:
            if upsert:
                upsert_inventory_item(
                    conn, supplier_id,
                    it["name"], int(it["qty"]),
                    it["unit"], float(it["unit_price"]),
                    it["category"],
                    merge_qty=merge_qty,
                )
            else:
                add_inventory_item(
                    conn, supplier_id,
                    it["name"], int(it["qty"]),
                    it["unit"], float(it["unit_price"]),
                    it["category"],
                )

def update_inventory_qty(conn: sqlite3.Connection,
                         supplier_id: int,
                         name: str,
                         qty_delta: int) -> None:
    """
    Increment (or decrement) quantity for a given item.
    """
    cur = conn.cursor()
    cur.execute("""
        UPDATE inventory
        SET qty = qty + ?
        WHERE supplier_id = ? AND name = ?;
    """, (qty_delta, supplier_id, name))
    conn.commit()

def delete_inventory_item(conn: sqlite3.Connection,
                          supplier_id: int,
                          name: str) -> None:
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM inventory
        WHERE supplier_id = ? AND name = ?;
    """, (supplier_id, name))
    conn.commit()

def get_inventory(conn: sqlite3.Connection,
                  supplier_id: int) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("""
        SELECT name, qty, unit, unit_price, category
        FROM inventory
        WHERE supplier_id = ?
        ORDER BY name;
    """, (supplier_id,))
    rows = cur.fetchall()
    return [dict(r) for r in rows]

def get_inventory_by_key(conn: sqlite3.Connection,
                         supplier_key: str) -> List[Dict[str, Any]]:
    """
    Convenience: fetch inventory by supplier key instead of id.
    """
    sid = get_supplier_id_by_key(conn, supplier_key)
    if sid is None:
        return []
    return get_inventory(conn, sid)

# ----------------------------
# Backward-compatibility aliases
# ----------------------------

# Some older codebases may call these names; keep them working.
def create_inventory_item(conn, supplier_id, name, qty, unit, unit_price, category):
    return add_inventory_item(conn, supplier_id, name, qty, unit, unit_price, category)

def add_item_to_inventory(conn, supplier_id, name, qty, unit, unit_price, category):
    return upsert_inventory_item(conn, supplier_id, name, qty, unit, unit_price, category, merge_qty=True)

def insert_inventory(conn, supplier_id, name, qty, unit, unit_price, category):
    return add_inventory_item(conn, supplier_id, name, qty, unit, unit_price, category)

def ensure_supplier_by_key(conn, key, lat, lon, label, base_lead_h, radius_km, delivery_mode):
    return ensure_supplier(conn, key, lat, lon, label, base_lead_h, radius_km, delivery_mode)

def get_db(db_path: str) -> sqlite3.Connection:
    """Alias for connect() used by some scripts."""
    return connect(db_path)
