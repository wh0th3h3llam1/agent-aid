# agents/need_agent.py
import os, json, asyncio, uuid, time
from typing import List, Tuple, Dict, Any
from collections import defaultdict

from uagents import Agent, Context
from agents.aid_protocol import (
    AidProtocol, QuoteRequest, QuoteResponse, Accept, AllocationNotice, Item, Geo
)

# ---------- telemetry helper (POST to FastAPI ingest) ----------
import httpx
TELEMETRY_URL = os.getenv("TELEMETRY_URL", "http://127.0.0.1:8088/ingest")

async def emit(ev: dict):
    try:
        async with httpx.AsyncClient(timeout=2) as c:
            await c.post(TELEMETRY_URL, json=ev)
    except Exception:
        # telemetry is best-effort; never break the flow
        pass

# ---------- optional intel (Bright Data -> Elastic) ----------
try:
    from intel.intel_client import fetch_intel as _fetch_intel  # optional module
except Exception:
    def _fetch_intel(lat: float, lon: float, radius_km: float = 25.0, horizon_min: int = 180):
        return {"count": 0, "road_block_count": 0, "weather_worst_severity": 0, "nearby_inventory": []}

# ---------- config ----------
NEEDER_NAME = os.getenv("NEEDER_NAME", "need_agent_berkeley_1")
NEEDER_SEED = os.getenv("NEEDER_SEED", "need_agent_berkeley_1_demo_seed")
NEEDER_PORT = int(os.getenv("NEEDER_PORT", "8000"))
ENDPOINT = [f"http://127.0.0.1:{NEEDER_PORT}/submit"]

SUPPLY_ADDRESSES = [a.strip() for a in os.getenv("SUPPLY_ADDRS", "").split(",") if a.strip()]

# Wait windows to collect multiple quotes before allocating
QUOTE_WAIT_S = float(os.getenv("QUOTE_WAIT_S", "3.0"))        # delay after first valid quote
QUOTE_MAX_WAIT_S = float(os.getenv("QUOTE_MAX_WAIT_S", "9.0"))  # absolute maximum from first quote

agent = Agent(name=NEEDER_NAME, seed=NEEDER_SEED, port=NEEDER_PORT, endpoint=ENDPOINT)

# ---------- scoring ----------
def score_with_intel(resp: QuoteResponse) -> float:
    """Combine coverage & price, lightly penalize risky intel (roads/weather)."""
    baseline = max(float(resp.total_cost or 1.0), 1.0)
    price_score = max(0.0, min(1.0, 2000.0 / baseline))
    cov = float(resp.coverage_ratio or 0.0)

    need_lat = float(os.getenv("NEED_LAT", "37.8715"))
    need_lon = float(os.getenv("NEED_LON", "-122.2730"))
    intel = _fetch_intel(need_lat, need_lon, radius_km=25.0, horizon_min=180)
    risk = 0.04 * float(intel.get("road_block_count", 0)) + 0.06 * float(intel.get("weather_worst_severity", 0))

    raw = 0.6 * cov + 0.4 * price_score
    return round(max(0.0, raw - risk), 4)

# ---------- lifecycle ----------
@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"[{NEEDER_NAME}] Address: {agent.address}")
    if not SUPPLY_ADDRESSES:
        ctx.logger.warning("No supply addresses set. Provide env SUPPLY_ADDRS='agent1...,agent1...'")
    await asyncio.sleep(0.8)
    await send_need(ctx)

async def send_need(ctx: Context):
    need_id = f"need_{uuid.uuid4().hex[:6]}"

    lat = float(os.getenv("NEED_LAT", "37.8715"))
    lon = float(os.getenv("NEED_LON", "-122.2730"))
    label = os.getenv("NEED_LABEL", "123 Main St, Berkeley")
    priority = os.getenv("NEED_PRIORITY", "critical")
    max_eta = float(os.getenv("NEED_MAX_ETA_H", "6"))

    items_json = os.getenv("NEED_ITEMS_JSON", '[{"name":"blanket","qty":200,"unit":"ea"}]')
    try:
        req_items = [Item(**x) for x in json.loads(items_json)]
    except Exception as e:
        ctx.logger.error(f"Invalid NEED_ITEMS_JSON: {e}")
        req_items = [Item(name="blanket", qty=200, unit="ea")]

    req = QuoteRequest(
        need_id=need_id,
        location=Geo(lat=lat, lon=lon, label=label),
        items=req_items,
        priority=priority,
        max_eta_hours=max_eta,
    )

    ctx.logger.info(f"Broadcasting QuoteRequest for {need_id} to {len(SUPPLY_ADDRESSES)} suppliers")
    for addr in SUPPLY_ADDRESSES:
        await ctx.send(addr, req)

    # telemetry
    await emit({"ts": time.time(), "agent_type":"needer","agent_id": NEEDER_NAME,
                "event_type":"quote_request","need_id": need_id, "lat": lat, "lon": lon})

    # persist ephemeral state
    try:
        requested_items = [it.model_dump() for it in req_items]  # pydantic v2
    except AttributeError:
        requested_items = [it.dict() for it in req_items]        # pydantic v1
    now = time.time()
    ctx.storage.set("awaiting_need", need_id)
    ctx.storage.set("quotes", [])
    ctx.storage.set("requested_items", requested_items)
    ctx.storage.set("alloc_start_ts", now)
    ctx.storage.set("alloc_first_deadline", now + QUOTE_WAIT_S)
    ctx.storage.set("alloc_final_deadline", now + QUOTE_MAX_WAIT_S)
    ctx.storage.set("remaining_needed", {it["name"].lower(): int(it["qty"]) for it in requested_items})

# ---------- quote collection with gather window ----------
_gather_task = None

def _now() -> float:
    return time.time()

async def _gather_then_allocate(ctx: Context):
    """Wait QUOTE_WAIT_S (bounded by QUOTE_MAX_WAIT_S) after first valid quote, then allocate."""
    first_ts = ctx.storage.get("first_quote_ts") or _now()
    deadline = min(first_ts + QUOTE_MAX_WAIT_S, _now() + QUOTE_WAIT_S)
    await asyncio.sleep(max(0.0, deadline - _now()))

    need_id = ctx.storage.get("awaiting_need")
    quotes: List[Dict[str, Any]] = ctx.storage.get("quotes") or []
    valid = [q for q in quotes if q["resp"].get("ok")]
    if need_id and valid:
        await allocate_and_accept(ctx)

@AidProtocol.on_message(model=QuoteResponse)
async def on_quote(ctx: Context, sender: str, resp: QuoteResponse):
    need_id = ctx.storage.get("awaiting_need")
    if not need_id or resp.need_id != need_id:
        return

    quotes: List[Dict[str, Any]] = ctx.storage.get("quotes") or []
    if resp.ok:
        sc = score_with_intel(resp)
        try:
            resp_dict = resp.model_dump()
        except AttributeError:
            resp_dict = resp.dict()
        quotes.append({"score": sc, "resp": resp_dict, "sender": sender})
        ctx.logger.info(
            f"Quote from {sender} | cost=${resp.total_cost} | eta={resp.eta_hours}h | "
            f"cov={resp.coverage_ratio} | score={sc}"
        )
        # telemetry
        await emit({"ts": time.time(), "agent_type":"needer","agent_id": NEEDER_NAME,
                    "event_type":"quote_response","need_id": resp.need_id,"supplier_id": resp.supplier_id,
                    "duration_ms": float((resp.eta_hours or 0)*3600*1000),
                    "meta":{"total_cost": resp.total_cost, "coverage": resp.coverage_ratio}})

        # mark first-quote arrival and start single gather task
        if ctx.storage.get("first_quote_ts") is None:
            ctx.storage.set("first_quote_ts", _now())

        global _gather_task
        if _gather_task is None or _gather_task.done():
            _gather_task = asyncio.create_task(_gather_then_allocate(ctx))
    else:
        ctx.logger.info(f"Rejected by {sender}: {resp.reason}")

    ctx.storage.set("quotes", quotes)

# ---------- allocation ----------
def _deserialize_items(dicts: List[Dict[str, Any]]) -> List[Item]:
    out = []
    for d in dicts or []:
        try:
            out.append(Item(**d))
        except Exception:
            pass
    return out

async def allocate_and_accept(ctx: Context):
    need_id = ctx.storage.get("awaiting_need")
    if not need_id:
        return

    quotes: List[Dict[str, Any]] = ctx.storage.get("quotes") or []
    valid = [q for q in quotes if q["resp"].get("ok")]
    if not valid:
        return

    requested_dicts = ctx.storage.get("requested_items") or []
    requested = _deserialize_items(requested_dicts) or [Item(name="blanket", qty=200, unit="ea")]
    remaining_needed: Dict[str, int] = ctx.storage.get("remaining_needed") or {it.name.lower(): it.qty for it in requested}

    per_supplier: Dict[str, Dict[str, int]] = defaultdict(dict)
    supplier_sender_addr: Dict[str, str] = {}
    supplier_items_meta: Dict[str, Dict[str, Tuple[str, float]]] = defaultdict(dict)

    # prefer higher score first
    for q in sorted(valid, key=lambda q: -q["score"]):
        resp = q["resp"]
        sid = resp["supplier_id"]
        supplier_sender_addr[sid] = q["sender"]
        for it in resp.get("items", []) or []:
            name = str(it["name"]).lower()
            offer_qty = int(it.get("qty") or 0)
            if offer_qty <= 0:
                continue
            need_qty = int(remaining_needed.get(name, 0))
            if need_qty <= 0:
                continue
            take = min(offer_qty, need_qty)
            if take > 0:
                per_supplier[sid][name] = per_supplier[sid].get(name, 0) + take
                remaining_needed[name] = need_qty - take
                supplier_items_meta[sid][name] = (it.get("unit"), float(it.get("unit_price") or 0.0))
        if all(qty <= 0 for qty in remaining_needed.values()):
            break

    accepts_sent = 0
    for sid, items_map in per_supplier.items():
        acc_items: List[Item] = []
        for name, qty in items_map.items():
            if qty <= 0:
                continue
            unit, price = supplier_items_meta[sid].get(name, (None, 0.0))
            acc_items.append(Item(name=name, qty=qty, unit=unit, unit_price=price))
        if not acc_items:
            continue
        # IMPORTANT: use ctx.send (not agent.send)
        await ctx.send(supplier_sender_addr[sid], Accept(
            need_id=need_id, supplier_id=sid, accept=True, items=acc_items
        ))
        accepts_sent += 1
        await emit({"ts": time.time(), "agent_type":"needer","agent_id": NEEDER_NAME,
                    "event_type":"accept_sent","need_id": need_id,"supplier_id": sid})
        ctx.logger.info(f"ACCEPT → {sid}: " + ", ".join([f"{i.name}:{i.qty}" for i in acc_items]))

    ctx.storage.set("remaining_needed", remaining_needed)

    # If everything is filled, clear state
    if accepts_sent > 0 and all(qty <= 0 for qty in remaining_needed.values()):
        for k in ("awaiting_need","quotes","requested_items","alloc_start_ts",
                  "alloc_first_deadline","alloc_final_deadline","remaining_needed","first_quote_ts"):
            try:
                if hasattr(ctx.storage, "remove"):
                    ctx.storage.remove(k)
                else:
                    ctx.storage.set(k, None)
            except Exception:
                ctx.storage.set(k, None)

# ---------- final confirmation ----------
@AidProtocol.on_message(model=AllocationNotice)
async def on_allocation(ctx: Context, sender: str, msg: AllocationNotice):
    summary = ", ".join([f"{i.name}:{i.qty}" for i in msg.items])
    ctx.logger.info(f"CONFIRMED by {msg.supplier_id}: {summary} ({msg.note or 'final allocation'})")
    await emit({"ts": time.time(), "agent_type":"needer","agent_id": NEEDER_NAME,
                "event_type":"allocation_notice","need_id": msg.need_id,"supplier_id": msg.supplier_id,
                "meta":{"items":[{"name":i.name,"qty":i.qty} for i in msg.items]}})

agent.include(AidProtocol)

if __name__ == "__main__":
    agent.run()
