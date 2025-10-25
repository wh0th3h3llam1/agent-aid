
import os
import json
import math
from typing import List, Dict, Any

from uagents import Agent, Context
from agents.aid_protocol import (
    AidProtocol,
    QuoteRequest,
    QuoteResponse,
    Accept,
    AllocationNotice,
    Item,
    Geo,
)

# ---- DB helpers (from services/inventory_db.py) ----
from services.inventory_db import (
    connect,
    ensure_supplier,
    get_supplier_config,
    get_inventory,
    offer_for_request,
    deduct_allocation,
)

# ---------- CONFIG ----------
DB_PATH = os.getenv("INV_DB_PATH", "db/agent_aid.db")

SUPPLIER_NAME = os.getenv("SUPPLIER_NAME", "supply_sf_store_1")
SUPPLIER_SEED = os.getenv("SUPPLIER_SEED", "supply_sf_store_1_demo_seed")
SUPPLIER_PORT = int(os.getenv("SUPPLIER_PORT", "8001"))

# Optional public endpoint override (e.g., ngrok); otherwise serve local
_endpoint_env = os.getenv("ENDPOINT_JSON")
if _endpoint_env:
    try:
        ENDPOINT = json.loads(_endpoint_env)
    except Exception:
        ENDPOINT = [f"http://127.0.0.1:{SUPPLIER_PORT}/submit"]
else:
    ENDPOINT = [f"http://127.0.0.1:{SUPPLIER_PORT}/submit"]

# Defaults used only if supplier row doesn’t exist yet
DEFAULT_CFG = dict(
    lat=37.78,
    lon=-122.42,
    label="SF Depot",
    base_lead_h=1.5,
    radius_km=120.0,
    delivery_mode="truck",
)

# ---------- Agent + DB ----------
agent = Agent(name=SUPPLIER_NAME, seed=SUPPLIER_SEED, port=SUPPLIER_PORT, endpoint=ENDPOINT)
CONN = connect(DB_PATH)
SUPPLIER_ID: int | None = None
CFG: Dict[str, Any] = {}

# ---------- Utils ----------
def haversine_km(a: Geo, b: Geo) -> float:
    """Distance in km."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [a.lat, a.lon, b.lat, b.lon])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

def _cfg_geo() -> Geo:
    return Geo(lat=float(CFG["lat"]), lon=float(CFG["lon"]), label=CFG.get("label"))

# ---------- Lifecycle ----------
@agent.on_event("startup")
async def on_start(ctx: Context):
    """
    Ensure supplier row exists, log current address + inventory.
    Inventory and config are always read fresh from DB during requests.
    """
    global SUPPLIER_ID, CFG
    SUPPLIER_ID = ensure_supplier(
        CONN,
        SUPPLIER_NAME,
        float(os.getenv("SUPPLIER_LAT", DEFAULT_CFG["lat"])),
        float(os.getenv("SUPPLIER_LON", DEFAULT_CFG["lon"])),
        os.getenv("SUPPLIER_LABEL", DEFAULT_CFG["label"]),
        float(os.getenv("SUPPLIER_LEAD_H", DEFAULT_CFG["base_lead_h"])),
        float(os.getenv("SUPPLIER_RADIUS_KM", DEFAULT_CFG["radius_km"])),
        os.getenv("SUPPLIER_DELIVERY_MODE", DEFAULT_CFG["delivery_mode"]),
    )
    CFG = get_supplier_config(CONN, SUPPLIER_NAME) or {}
    inv = get_inventory(CONN, SUPPLIER_ID)

    ctx.logger.info(f"[{SUPPLIER_NAME}] Address: {agent.address}")
    ctx.logger.info(
        "Inventory: " + (", ".join([f"{row['name']}:{row['qty']}" for row in inv]) if inv else "(empty)")
    )

# ---------- Protocol Handlers ----------
@AidProtocol.on_message(model=QuoteRequest, replies=QuoteResponse)
async def on_quote(ctx: Context, sender: str, req: QuoteRequest):
    """
    Build a quote from current DB stock. Only offer what's available.
    Reject if out of radius or ETA > SLA.
    """
    # load latest config each time
    global CFG
    CFG = get_supplier_config(CONN, SUPPLIER_NAME) or CFG

    # radius check
    d_km = haversine_km(req.location, _cfg_geo())
    if d_km > float(CFG["radius_km"]):
        await ctx.send(
            sender,
            QuoteResponse(
                need_id=req.need_id,
                supplier_id=SUPPLIER_NAME,
                ok=False,
                reason=f"out_of_radius_{int(d_km)}km",
            ),
        )
        return

    # DB computes coverage + per-item offer
    requested = [{"name": it.name, "qty": int(it.qty)} for it in (req.items or [])]
    offered, cov = offer_for_request(CONN, SUPPLIER_ID, requested)

    if cov <= 0.0 or not offered:
        await ctx.send(
            sender,
            QuoteResponse(
                need_id=req.need_id, supplier_id=SUPPLIER_NAME, ok=False, reason="no_coverage"
            ),
        )
        return

    # pricing + ETA
    base_cost = sum(float(it.get("unit_price", 0.0)) * int(it["qty"]) for it in offered)
    travel_eta = d_km / 40.0  # ~40km/h conservative
    eta = round(float(CFG["base_lead_h"]) + travel_eta, 2)

    if req.max_eta_hours is not None and eta > float(req.max_eta_hours):
        await ctx.send(
            sender,
            QuoteResponse(
                need_id=req.need_id,
                supplier_id=SUPPLIER_NAME,
                ok=False,
                reason=f"eta_exceeds_sla_{eta}h",
            ),
        )
        return

    priority = (req.priority or "medium").lower()
    mod = {"critical": 0.90, "high": 0.95, "medium": 1.00, "low": 1.05}.get(priority, 1.00)
    total = round(base_cost * mod, 2)

    # convert dicts -> Item models
    offered_items: List[Item] = [
        Item(
            name=o["name"],
            qty=int(o["qty"]),
            unit=o.get("unit"),
            unit_price=float(o.get("unit_price", 0.0)),
        )
        for o in offered
    ]

    await ctx.send(
        sender,
        QuoteResponse(
            need_id=req.need_id,
            supplier_id=SUPPLIER_NAME,
            ok=True,
            coverage_ratio=round(cov, 3),
            eta_hours=eta,
            total_cost=total,
            items=offered_items,
            terms=f"delivery:{CFG['delivery_mode']};priority:{priority}",
        ),
    )
    ctx.logger.info(
        f"[{SUPPLIER_NAME}] Quote → {sender} offered="
        + ", ".join([f"{i.name}:{i.qty}" for i in offered_items])
        + f" eta={eta}h total=${total}"
    )

@AidProtocol.on_message(model=Accept, replies=AllocationNotice)
async def on_accept(ctx: Context, sender: str, msg: Accept):
    """
    Deduct the accepted quantities **atomically in the database**
    and confirm with an AllocationNotice.
    """
    # Build item dicts for DB deduction
    items = [
        {
            "name": it.name,
            "qty": int(it.qty or 0),
            "unit": it.unit,
            "unit_price": float(it.unit_price or 0.0),
        }
        for it in (msg.items or [])
    ]

    # atomic deduction in DB
    deduct_allocation(CONN, SUPPLIER_ID, items)

    # reply with what we confirm allocated
    notice_items = [
        Item(name=i["name"], qty=i["qty"], unit=i.get("unit"), unit_price=i.get("unit_price", 0.0))
        for i in items
    ]
    await ctx.send(
        sender,
        AllocationNotice(
            need_id=msg.need_id,
            supplier_id=SUPPLIER_NAME,
            items=notice_items,
            note="allocation confirmed (DB-deducted)",
        ),
    )
    ctx.logger.info(
        f"[{SUPPLIER_NAME}] Allocation confirmed for {sender}: "
        + ", ".join([f"{i.name}:{i.qty}" for i in notice_items])
    )

# include the protocol and run
agent.include(AidProtocol)

if __name__ == "__main__":
    agent.run()
