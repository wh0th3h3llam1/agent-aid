import os, json, sqlite3, argparse
from services.inventory_db import (
    connect,
    ensure_supplier,
    upsert_item,
    get_inventory,
    get_supplier_config,
)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", default=os.getenv("INV_DB_PATH","db/agent_aid.db"))
    sub = p.add_subparsers(dest="cmd", required=True)

    add_sup = sub.add_parser("add-supplier")
    add_sup.add_argument("--name", required=True)
    add_sup.add_argument("--lat", type=float, required=True)
    add_sup.add_argument("--lon", type=float, required=True)
    add_sup.add_argument("--label", default="")
    add_sup.add_argument("--lead", type=float, default=1.5)
    add_sup.add_argument("--radius", type=float, default=120.0)
    add_sup.add_argument("--mode", default="truck")

    stock = sub.add_parser("stock")
    stock.add_argument("--name", required=True)
    stock.add_argument("--items", required=True, help='JSON e.g. \'[{"name":"blanket","qty":200,"unit":"ea","unit_price":8}]\'')
    args = p.parse_args()

    conn = connect(args.db)

    if args.cmd == "add-supplier":
        sid = ensure_supplier(conn, args.name, args.lat, args.lon, args.label, args.lead, args.radius, args.mode)
        cfg = get_supplier_config(conn, args.name)
        print("Added/Ensured supplier:", cfg)
    elif args.cmd == "stock":
        items = json.loads(args.items)
        cfg = get_supplier_config(conn, args.name)
        if not cfg:
            raise SystemExit("Supplier does not exist. Create it first with add-supplier.")
        sid = cfg["id"]
        for it in items:
            upsert_item(conn, sid, it["name"], int(it.get("qty",0)), it.get("unit"), float(it.get("unit_price",0.0)))
        print("Inventory now:", get_inventory(conn, sid))

if __name__ == "__main__":
    main()
