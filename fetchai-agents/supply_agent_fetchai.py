#!/usr/bin/env python3
"""
Supply Agent for Fetch.ai Agentverse
Registers on Almanac and responds to quote requests
"""
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
import os
import math

# Models for communication
class QuoteRequest(Model):
    request_id: str
    items: list
    quantity: int
    location: dict
    priority: str

class QuoteResponse(Model):
    request_id: str
    supplier_id: str
    supplier_name: str
    items: list
    total_cost: float
    eta_hours: float
    coverage: float
    delivery_mode: str
    available: bool

# Agent configuration
SUPPLIER_NAME = os.getenv("SUPPLIER_NAME", "medical_emergency_depot")
SUPPLIER_LABEL = os.getenv("SUPPLIER_LABEL", "Medical Emergency Depot")
SEED = os.getenv("AGENT_SEED", "supply_medical_seed_phrase_123")

# Create agent with seed for consistent address
agent = Agent(
    name=SUPPLIER_NAME,
    seed=SEED,
    port=8001,
    endpoint=["http://localhost:8001/submit"],
)

# Fund agent if needed (for Almanac registration)
fund_agent_if_low(agent.wallet.address())

# Inventory (in production, this would be from database)
INVENTORY = {
    "blankets": {"qty": 300, "price": 30.0},
    "first aid kit": {"qty": 100, "price": 50.0},
    "water bottles": {"qty": 500, "price": 2.0},
    "flashlight": {"qty": 150, "price": 15.0}
}

# Location
LOCATION = {
    "lat": float(os.getenv("SUPPLIER_LAT", "37.7749")),
    "lon": float(os.getenv("SUPPLIER_LON", "-122.4194"))
}

RADIUS_KM = float(os.getenv("SUPPLIER_RADIUS_KM", "200.0"))
BASE_ETA_HOURS = float(os.getenv("SUPPLIER_LEAD_H", "1.0"))
DELIVERY_MODE = os.getenv("SUPPLIER_DELIVERY_MODE", "ambulance")

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km"""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

# Protocol for quote requests
quote_protocol = Protocol("QuoteProtocol")

@quote_protocol.on_message(model=QuoteRequest, replies=QuoteResponse)
async def handle_quote_request(ctx: Context, sender: str, msg: QuoteRequest):
    """Handle incoming quote requests"""
    ctx.logger.info(f"📦 Received quote request: {msg.request_id}")
    ctx.logger.info(f"   Items: {msg.items}")
    ctx.logger.info(f"   From: {sender[:20]}...")
    
    # Check distance
    req_coords = msg.location.get("coordinates", {})
    if req_coords:
        req_lat = req_coords.get("latitude", 0)
        req_lon = req_coords.get("longitude", 0)
        distance = haversine_km(LOCATION["lat"], LOCATION["lon"], req_lat, req_lon)
        
        ctx.logger.info(f"   Distance: {distance:.1f} km")
        
        if distance > RADIUS_KM:
            ctx.logger.info(f"   ❌ Out of radius ({RADIUS_KM} km)")
            await ctx.send(sender, QuoteResponse(
                request_id=msg.request_id,
                supplier_id=SUPPLIER_NAME,
                supplier_name=SUPPLIER_LABEL,
                items=[],
                total_cost=0,
                eta_hours=0,
                coverage=0,
                delivery_mode=DELIVERY_MODE,
                available=False
            ))
            return
    
    # Check inventory and build quote
    quoted_items = []
    total_cost = 0.0
    
    for item_name in msg.items:
        item_lower = item_name.lower()
        if item_lower in INVENTORY:
            inv_item = INVENTORY[item_lower]
            available_qty = inv_item["qty"]
            requested_qty = msg.quantity
            
            if available_qty >= requested_qty:
                quoted_items.append({
                    "name": item_name,
                    "qty": requested_qty,
                    "unit_price": inv_item["price"]
                })
                total_cost += requested_qty * inv_item["price"]
    
    if not quoted_items:
        ctx.logger.info(f"   ❌ No inventory available")
        await ctx.send(sender, QuoteResponse(
            request_id=msg.request_id,
            supplier_id=SUPPLIER_NAME,
            supplier_name=SUPPLIER_LABEL,
            items=[],
            total_cost=0,
            eta_hours=0,
            coverage=0,
            delivery_mode=DELIVERY_MODE,
            available=False
        ))
        return
    
    # Calculate ETA
    distance = haversine_km(LOCATION["lat"], LOCATION["lon"], req_lat, req_lon) if req_coords else 0
    travel_time = distance / 60.0  # Assume 60 km/h
    eta_hours = BASE_ETA_HOURS + travel_time
    
    # Calculate coverage
    coverage = len(quoted_items) / len(msg.items)
    
    ctx.logger.info(f"   ✅ Quote ready: ${total_cost:.2f}, ETA: {eta_hours:.1f}h")
    
    # Send quote
    await ctx.send(sender, QuoteResponse(
        request_id=msg.request_id,
        supplier_id=SUPPLIER_NAME,
        supplier_name=SUPPLIER_LABEL,
        items=quoted_items,
        total_cost=total_cost,
        eta_hours=eta_hours,
        coverage=coverage,
        delivery_mode=DELIVERY_MODE,
        available=True
    ))

agent.include(quote_protocol)

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🚀 {SUPPLIER_LABEL} started")
    ctx.logger.info(f"   Address: {agent.address}")
    ctx.logger.info(f"   Inventory: {list(INVENTORY.keys())}")
    ctx.logger.info(f"   Location: ({LOCATION['lat']}, {LOCATION['lon']})")
    ctx.logger.info(f"   Radius: {RADIUS_KM} km")

if __name__ == "__main__":
    agent.run()
