from typing import List, Optional, Literal
from uagents import Model, Protocol

AidProtocol = Protocol(name="aid_market", version="2.0.0")

Priority = Literal["low", "medium", "high", "critical"]

class Item(Model):
    name: str
    qty: int
    unit: Optional[str] = None
    unit_price: Optional[float] = None  # in responses/quotes

class Geo(Model):
    lat: float
    lon: float
    label: Optional[str] = None

class QuoteRequest(Model):
    need_id: str
    location: Geo
    items: List[Item]
    priority: Priority
    max_eta_hours: float

class QuoteResponse(Model):
    need_id: str
    supplier_id: str
    ok: bool
    reason: Optional[str] = None
    coverage_ratio: Optional[float] = None
    eta_hours: Optional[float] = None
    total_cost: Optional[float] = None
    # Items here reflect the supplier's **offered quantities** (capped by inventory)
    items: Optional[List[Item]] = None
    terms: Optional[str] = None

class Accept(Model):
    need_id: str
    supplier_id: str
    accept: bool
    # Per-supplier allocation the needer wants this supplier to fulfill (partial allowed)
    items: List[Item]

class AllocationNotice(Model):
    """Supplier→Needer: final confirmed allocation if multiple accepts exceed stock."""
    need_id: str
    supplier_id: str
    items: List[Item]   # confirmed allocated quantities (may be less than requested)
    note: Optional[str] = None

class Restock(Model):
    """Add quantities to inventory (admin use)."""
    secret: str                 # shared secret
    items: List[Item]           # name + qty (+ optional unit / unit_price)

class AdjustInventory(Model):
    """Arbitrary delta adjustment (+/-) (admin use)."""
    secret: str
    items: List[Item]           # when qty is negative -> deduct

class InventoryStatus(Model):
    """Echo inventory after change or on query."""
    supplier_id: str
    inventory: List[Item]
    note: Optional[str] = None

class ErrorMessage(Model):
    message: str


# doc-only; no logic
@AidProtocol.on_message(model=QuoteRequest, replies=QuoteResponse)
async def _req_to_resp(_, __, ___): pass

@AidProtocol.on_message(model=Accept, replies=AllocationNotice)
async def _acc_to_alloc(_, __, ___): pass
