PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS suppliers (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT UNIQUE NOT NULL,
  lat           REAL NOT NULL,
  lon           REAL NOT NULL,
  label         TEXT,
  base_lead_h   REAL NOT NULL DEFAULT 1.5,
  radius_km     REAL NOT NULL DEFAULT 120.0,
  delivery_mode TEXT NOT NULL DEFAULT 'truck'
);

CREATE TABLE IF NOT EXISTS items (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  supplier_id  INTEGER NOT NULL,
  name         TEXT NOT NULL,
  unit         TEXT,
  unit_price   REAL NOT NULL DEFAULT 0.0,
  qty          INTEGER NOT NULL DEFAULT 0,
  category     TEXT DEFAULT 'general',
  UNIQUE(supplier_id, name),
  FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
);
