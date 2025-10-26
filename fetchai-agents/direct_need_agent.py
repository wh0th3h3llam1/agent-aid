#!/usr/bin/env python3
"""
Direct Need Agent - Communicates directly with Supply Agent
Uses Chat Protocol for Fetch.ai Agentverse deployment
No intermediary required
"""

import os
import json
import asyncio
from typing import cast, Dict, List
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

class FinalResult(Model):
    request_id: str
    best_supplier: str
    quantity: int
    eta_hours: float
    coverage_pct: float
    location: str

# Agent configuration
AGENT_NAME = "Direct Need Agent"
SEED_PHRASE = "direct_need_agent_seed_phrase_demo_2024"
SUPPLY_AGENT_ADDRESS = "agent1qfpqn9jhvp9j85c0w7jertw7aq42saqf8k4mknkwqk7x8qx7t8syc7egdl"  # Update this

# Create agent
agent = Agent(
    name=AGENT_NAME,
    seed=SEED_PHRASE,
    port=8000,
    endpoint=["http://localhost:8000/submit"],
)

# Fund agent if needed (for testnet)
fund_agent_if_low(agent.wallet.address())

# Storage
active_requests = {}
collected_quotes = {}

print(f"\n{'='*80}")
print(f"🚨 {AGENT_NAME}")
print(f"{'='*80}")
print(f"Agent Address: {agent.address}")
print(f"Supply Agent: {SUPPLY_AGENT_ADDRESS}")
print(f"{'='*80}\n")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Need Agent started: {agent.address}")
    ctx.logger.info(f"Will communicate with Supply Agent: {SUPPLY_AGENT_ADDRESS}")

@agent.on_message(model=QuoteResponse)
async def handle_quote_response(ctx: Context, sender: str, msg: QuoteResponse):
    """Handle quote response from supply agent"""
    ctx.logger.info(f"💰 Quote received from {sender}")
    ctx.logger.info(f"   Request ID: {msg.request_id}")
    ctx.logger.info(f"   Quantity: {msg.quantity_offered}")
    ctx.logger.info(f"   ETA: {msg.eta_hours} hours")
    ctx.logger.info(f"   Coverage: {msg.coverage_pct}%")
    
    # Store quote
    if msg.request_id not in collected_quotes:
        collected_quotes[msg.request_id] = []
    
    collected_quotes[msg.request_id].append({
        "supplier": msg.supplier,
        "supplier_address": msg.supplier_address,
        "quantity_offered": msg.quantity_offered,
        "eta_hours": msg.eta_hours,
        "coverage_pct": msg.coverage_pct,
        "timestamp": msg.timestamp
    })
    
    ctx.logger.info(f"✅ Quote stored. Total quotes for {msg.request_id}: {len(collected_quotes[msg.request_id])}")

@agent.on_interval(period=15.0)
async def evaluate_quotes(ctx: Context):
    """Periodically evaluate collected quotes"""
    for request_id, quotes in list(collected_quotes.items()):
        if len(quotes) > 0 and request_id in active_requests:
            request_data = active_requests[request_id]
            
            # Check if enough time has passed (10 seconds)
            request_time = datetime.fromisoformat(request_data["timestamp"])
            elapsed = (datetime.now() - request_time).total_seconds()
            
            if elapsed >= 10:
                ctx.logger.info(f"\n📊 Evaluating {len(quotes)} quote(s) for {request_id}")
                
                # Evaluate quotes
                best_quote = evaluate_best_quote(quotes, request_data["quantity"])
                
                ctx.logger.info(f"🏆 Best supplier: {best_quote['supplier']}")
                ctx.logger.info(f"   Quantity: {best_quote['quantity_offered']}")
                ctx.logger.info(f"   ETA: {best_quote['eta_hours']} hours")
                ctx.logger.info(f"   Score: {best_quote['score']:.1f}/100")
                
                # Clean up
                del collected_quotes[request_id]
                del active_requests[request_id]

def evaluate_best_quote(quotes: List[Dict], requested_qty: int) -> Dict:
    """Evaluate quotes based on quantity and ETA"""
    def score_quote(quote):
        # Quantity score (0-100)
        qty_score = min(quote["quantity_offered"] / requested_qty, 1.0) * 100
        
        # ETA score (0-100) - faster is better
        eta_score = max(0, 100 - (quote["eta_hours"] * 10))
        
        # Total score (equal weight)
        total_score = (qty_score * 0.5) + (eta_score * 0.5)
        return total_score
    
    # Score all quotes
    for quote in quotes:
        quote["score"] = score_quote(quote)
    
    # Sort by score
    sorted_quotes = sorted(quotes, key=lambda q: q["score"], reverse=True)
    return sorted_quotes[0]

# HTTP endpoint for receiving requests
@agent.on_rest_post("/request")
async def handle_http_request(ctx: Context, req: dict):
    """Handle HTTP request from external system"""
    try:
        message = req.get("message", "")
        ctx.logger.info(f"\n📨 HTTP Request received: {message}")
        
        # Parse message
        request_data = parse_request(message)
        request_id = f"REQ-{int(datetime.now().timestamp() * 1000)}"
        
        request_data["request_id"] = request_id
        request_data["timestamp"] = datetime.now().isoformat()
        
        # Store request
        active_requests[request_id] = request_data
        
        ctx.logger.info(f"✅ Request created: {request_id}")
        ctx.logger.info(f"   Items: {request_data['items']}")
        ctx.logger.info(f"   Quantity: {request_data['quantity']}")
        ctx.logger.info(f"   Location: {request_data['location']}")
        ctx.logger.info(f"   Priority: {request_data['priority']}")
        
        # Send quote request to supply agent
        quote_request = QuoteRequest(
            request_id=request_id,
            items=request_data["items"],
            quantity=request_data["quantity"],
            location=request_data["location"],
            priority=request_data["priority"],
            affected_people=request_data.get("affected_people", 0)
        )
        
        ctx.logger.info(f"📤 Sending quote request to supply agent...")
        await ctx.send(SUPPLY_AGENT_ADDRESS, quote_request)
        ctx.logger.info(f"✅ Quote request sent!")
        
        return {
            "status": "accepted",
            "request_id": request_id,
            "message": "Request is being processed. Waiting for supplier quotes..."
        }
        
    except Exception as e:
        ctx.logger.error(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}

def parse_request(message: str) -> dict:
    """Parse natural language request"""
    import re
    
    message_lower = message.lower()
    
    # Detect priority
    priority = "medium"
    if any(word in message_lower for word in ["critical", "urgent", "emergency"]):
        priority = "critical"
    elif "high" in message_lower:
        priority = "high"
    elif "low" in message_lower:
        priority = "low"
    
    # Extract items
    items = []
    item_keywords = {
        "blanket": "blankets",
        "water": "water bottles",
        "food": "food supplies",
        "medical": "medical supplies",
        "tent": "tents",
        "clothing": "clothing"
    }
    
    for keyword, item_name in item_keywords.items():
        if keyword in message_lower:
            items.append(item_name)
    
    if not items:
        items = ["emergency supplies"]
    
    # Extract quantity
    qty_match = re.search(r'(\d+)\s+(?:blanket|water|food|medical|supply|supplies|people)', message_lower)
    quantity = int(qty_match.group(1)) if qty_match else 50
    
    # Extract location
    location = "Location TBD"
    if "berkeley" in message_lower:
        location = "Berkeley, CA"
    elif "oakland" in message_lower:
        location = "Oakland, CA"
    elif "san francisco" in message_lower or "sf" in message_lower:
        location = "San Francisco, CA"
    
    # Extract affected people
    people_match = re.search(r'(\d+)\s+people', message_lower)
    affected_people = int(people_match.group(1)) if people_match else 0
    
    return {
        "items": items,
        "quantity": quantity,
        "location": location,
        "priority": priority,
        "affected_people": affected_people
    }

if __name__ == "__main__":
    agent.run()
