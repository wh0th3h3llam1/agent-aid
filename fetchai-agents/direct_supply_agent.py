#!/usr/bin/env python3
"""
Direct Supply Agent - Responds directly to Need Agent
Uses Chat Protocol for Fetch.ai Agentverse deployment
No intermediary required
"""

import os
from typing import List
from datetime import datetime
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Message Models
class QuoteRequest(Model):
    request_id: str
    items: List[str]
    quantity: int
    location: str
    priority: str
    affected_people: int

class QuoteResponse(Model):
    request_id: str
    supplier: str
    supplier_address: str
    quantity_offered: int
    eta_hours: float
    coverage_pct: float
    timestamp: str

# Agent configuration
AGENT_NAME = "Direct Supply Agent"
SEED_PHRASE = "direct_supply_agent_seed_phrase_demo_2024"
SUPPLIER_LOCATION = "SF Depot"

# Create agent
agent = Agent(
    name=AGENT_NAME,
    seed=SEED_PHRASE,
    port=8001,
    endpoint=["http://localhost:8001/submit"],
)

# Fund agent if needed (for testnet)
fund_agent_if_low(agent.wallet.address())

# Mock inventory
INVENTORY = {
    "blankets": {"available": 500, "unit": "ea"},
    "water bottles": {"available": 1000, "unit": "bottles"},
    "medical supplies": {"available": 200, "unit": "kits"},
    "food supplies": {"available": 800, "unit": "meals"},
    "shelter materials": {"available": 150, "unit": "sets"},
    "clothing": {"available": 300, "unit": "sets"},
    "tents": {"available": 50, "unit": "ea"},
    "medicine": {"available": 100, "unit": "kits"},
    "emergency supplies": {"available": 400, "unit": "units"}
}

# Location data
LOCATION_COORDS = {
    "berkeley": {"distance_km": 25},
    "oakland": {"distance_km": 20},
    "san francisco": {"distance_km": 5},
    "sf": {"distance_km": 5}
}

print(f"\n{'='*80}")
print(f"📦 {AGENT_NAME}")
print(f"{'='*80}")
print(f"Agent Address: {agent.address}")
print(f"Supplier Location: {SUPPLIER_LOCATION}")
print(f"Inventory Items: {len(INVENTORY)}")
print(f"Total Units: {sum(item['available'] for item in INVENTORY.values())}")
print(f"{'='*80}\n")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Supply Agent started: {agent.address}")
    ctx.logger.info(f"Supplier: {SUPPLIER_LOCATION}")
    ctx.logger.info(f"Inventory: {len(INVENTORY)} item types")

@agent.on_message(model=QuoteRequest)
async def handle_quote_request(ctx: Context, sender: str, msg: QuoteRequest):
    """Handle quote request from need agent"""
    ctx.logger.info(f"\n💰 Quote request received from {sender}")
    ctx.logger.info(f"   Request ID: {msg.request_id}")
    ctx.logger.info(f"   Items: {msg.items}")
    ctx.logger.info(f"   Quantity: {msg.quantity}")
    ctx.logger.info(f"   Location: {msg.location}")
    ctx.logger.info(f"   Priority: {msg.priority}")
    
    # Generate quote
    quote = generate_quote(msg.items, msg.quantity, msg.location, msg.priority)
    
    ctx.logger.info(f"✅ Quote generated:")
    ctx.logger.info(f"   Quantity offered: {quote['quantity_offered']}")
    ctx.logger.info(f"   ETA: {quote['eta_hours']} hours")
    ctx.logger.info(f"   Coverage: {quote['coverage_pct']:.1f}%")
    
    # Send quote response back to need agent
    quote_response = QuoteResponse(
        request_id=msg.request_id,
        supplier=SUPPLIER_LOCATION,
        supplier_address=agent.address,
        quantity_offered=quote["quantity_offered"],
        eta_hours=quote["eta_hours"],
        coverage_pct=quote["coverage_pct"],
        timestamp=datetime.now().isoformat()
    )
    
    ctx.logger.info(f"📤 Sending quote response to {sender}...")
    await ctx.send(sender, quote_response)
    ctx.logger.info(f"✅ Quote sent!")

def generate_quote(items: List[str], requested_qty: int, location: str, priority: str) -> dict:
    """Generate a quote based on inventory and location"""
    
    # Find matching items in inventory
    available_qty = 0
    for item in items:
        for inv_item, inv_data in INVENTORY.items():
            if item.lower() in inv_item or inv_item in item.lower():
                available_qty = max(available_qty, inv_data["available"])
                break
    
    # Determine quantity we can offer
    quantity_offered = min(requested_qty, available_qty)
    
    # Calculate distance
    location_lower = location.lower()
    distance_km = 30  # default
    
    for loc_key, loc_data in LOCATION_COORDS.items():
        if loc_key in location_lower:
            distance_km = loc_data["distance_km"]
            break
    
    # Calculate ETA
    base_lead_time = 1.5  # hours for preparation
    travel_time = distance_km / 40.0  # 40 km/h average speed
    eta_hours = base_lead_time + travel_time
    
    # Priority adjustment (faster for critical)
    if priority == "critical":
        eta_hours = eta_hours * 0.8  # 20% faster
    elif priority == "high":
        eta_hours = eta_hours * 0.9  # 10% faster
    
    eta_hours = round(eta_hours, 1)
    
    # Calculate coverage
    coverage_pct = (quantity_offered / requested_qty * 100) if requested_qty > 0 else 0
    
    return {
        "quantity_offered": quantity_offered,
        "eta_hours": eta_hours,
        "distance_km": distance_km,
        "coverage_pct": coverage_pct
    }

# HTTP endpoint for inventory check
@agent.on_rest_get("/inventory")
async def get_inventory(ctx: Context):
    """Return current inventory"""
    return {
        "supplier": SUPPLIER_LOCATION,
        "inventory": INVENTORY,
        "total_units": sum(item["available"] for item in INVENTORY.values())
    }

@agent.on_rest_get("/status")
async def get_status(ctx: Context):
    """Health check endpoint"""
    return {
        "status": "OK - Agent is running",
        "agent_name": AGENT_NAME,
        "agent_address": agent.address,
        "supplier_location": SUPPLIER_LOCATION,
        "inventory_items": len(INVENTORY),
        "total_units": sum(item["available"] for item in INVENTORY.values())
    }

if __name__ == "__main__":
    agent.run()
