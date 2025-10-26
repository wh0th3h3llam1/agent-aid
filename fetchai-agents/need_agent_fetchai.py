#!/usr/bin/env python3
"""
Need Agent for Fetch.ai Agentverse
Receives requests, broadcasts to suppliers, evaluates quotes
"""
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
import os

# Models
class DisasterRequest(Model):
    request_id: str
    items: list
    quantity: int
    location: dict
    priority: str
    contact: str
    victim_count: int

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

class NegotiationResult(Model):
    request_id: str
    selected_supplier: str
    selected_supplier_name: str
    total_cost: float
    eta_hours: float
    reasoning: str
    all_quotes_count: int

# Agent configuration
NEED_AGENT_NAME = os.getenv("NEED_AGENT_NAME", "need_agent_coordinator")
SEED = os.getenv("AGENT_SEED", "need_agent_seed_phrase_456")

# Create agent
agent = Agent(
    name=NEED_AGENT_NAME,
    seed=SEED,
    port=8000,
    endpoint=["http://localhost:8000/submit"],
)

fund_agent_if_low(agent.wallet.address())

# Store active requests and quotes
active_requests = {}
collected_quotes = {}

# Supplier addresses (set via environment or discovery)
SUPPLIER_ADDRESSES = os.getenv("SUPPLIER_ADDRESSES", "").split(",")

# Protocol
request_protocol = Protocol("RequestProtocol")

@request_protocol.on_message(model=DisasterRequest)
async def handle_disaster_request(ctx: Context, sender: str, msg: DisasterRequest):
    """Handle incoming disaster requests from coordinator"""
    ctx.logger.info(f"🚨 Received disaster request: {msg.request_id}")
    ctx.logger.info(f"   Items: {msg.items}")
    ctx.logger.info(f"   Priority: {msg.priority}")
    ctx.logger.info(f"   From: {sender[:20]}...")
    
    # Store request
    active_requests[msg.request_id] = {
        "request": msg,
        "sender": sender,
        "quotes_received": 0
    }
    collected_quotes[msg.request_id] = []
    
    # Broadcast to all suppliers
    quote_req = QuoteRequest(
        request_id=msg.request_id,
        items=msg.items,
        quantity=msg.quantity,
        location=msg.location,
        priority=msg.priority
    )
    
    ctx.logger.info(f"   📢 Broadcasting to {len(SUPPLIER_ADDRESSES)} suppliers...")
    for supplier_addr in SUPPLIER_ADDRESSES:
        if supplier_addr:
            try:
                await ctx.send(supplier_addr, quote_req)
                ctx.logger.info(f"      → Sent to {supplier_addr[:20]}...")
            except Exception as e:
                ctx.logger.error(f"      ✗ Failed to send to {supplier_addr[:20]}: {e}")
    
    # Wait for quotes (schedule evaluation)
    ctx.storage.set(f"eval_time_{msg.request_id}", ctx.storage.get("current_time", 0) + 15)

@request_protocol.on_message(model=QuoteResponse)
async def handle_quote_response(ctx: Context, sender: str, msg: QuoteResponse):
    """Handle quote responses from suppliers"""
    ctx.logger.info(f"💰 Received quote for {msg.request_id}")
    ctx.logger.info(f"   From: {msg.supplier_name}")
    ctx.logger.info(f"   Cost: ${msg.total_cost}, ETA: {msg.eta_hours}h")
    ctx.logger.info(f"   Available: {msg.available}")
    
    if msg.request_id in collected_quotes:
        collected_quotes[msg.request_id].append({
            "quote": msg,
            "sender": sender
        })
        active_requests[msg.request_id]["quotes_received"] += 1
        
        ctx.logger.info(f"   Total quotes: {len(collected_quotes[msg.request_id])}")

async def evaluate_quotes(ctx: Context, request_id: str):
    """Evaluate collected quotes and select best"""
    if request_id not in collected_quotes:
        return
    
    quotes = collected_quotes[request_id]
    if not quotes:
        ctx.logger.info(f"⚠️  No quotes for {request_id}")
        return
    
    ctx.logger.info(f"🤝 Evaluating {len(quotes)} quotes for {request_id}")
    
    # Filter available quotes
    available_quotes = [q for q in quotes if q["quote"].available]
    
    if not available_quotes:
        ctx.logger.info(f"   ❌ No available suppliers")
        return
    
    # Score each quote
    scored_quotes = []
    for q in available_quotes:
        quote = q["quote"]
        
        # Scoring: lower cost + faster ETA + better coverage
        cost_score = 1.0 / (1.0 + quote.total_cost / 1000.0)
        eta_score = 1.0 / (1.0 + quote.eta_hours / 10.0)
        coverage_score = quote.coverage
        
        total_score = 0.4 * cost_score + 0.3 * eta_score + 0.3 * coverage_score
        
        scored_quotes.append({
            "quote": quote,
            "sender": q["sender"],
            "score": total_score
        })
        
        ctx.logger.info(f"   📊 {quote.supplier_name}: Score={total_score:.3f}")
    
    # Select best
    best = max(scored_quotes, key=lambda x: x["score"])
    best_quote = best["quote"]
    
    ctx.logger.info(f"   ✅ Selected: {best_quote.supplier_name}")
    ctx.logger.info(f"      Cost: ${best_quote.total_cost}")
    ctx.logger.info(f"      ETA: {best_quote.eta_hours:.1f}h")
    ctx.logger.info(f"      Score: {best['score']:.3f}")
    
    # Send result back to coordinator
    if request_id in active_requests:
        coordinator = active_requests[request_id]["sender"]
        
        result = NegotiationResult(
            request_id=request_id,
            selected_supplier=best_quote.supplier_id,
            selected_supplier_name=best_quote.supplier_name,
            total_cost=best_quote.total_cost,
            eta_hours=best_quote.eta_hours,
            reasoning=f"Selected {best_quote.supplier_name} with score {best['score']:.3f}. "
                     f"Best balance of cost (${best_quote.total_cost}), "
                     f"speed ({best_quote.eta_hours:.1f}h), and coverage ({best_quote.coverage*100:.0f}%).",
            all_quotes_count=len(quotes)
        )
        
        await ctx.send(coordinator, result)
        ctx.logger.info(f"   📤 Sent result to coordinator")
        
        # Cleanup
        del active_requests[request_id]
        del collected_quotes[request_id]

agent.include(request_protocol)

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🤖 {NEED_AGENT_NAME} started")
    ctx.logger.info(f"   Address: {agent.address}")
    ctx.logger.info(f"   Suppliers: {len(SUPPLIER_ADDRESSES)}")

@agent.on_interval(period=10.0)
async def check_evaluations(ctx: Context):
    """Periodically check if it's time to evaluate quotes"""
    current_time = ctx.storage.get("current_time", 0)
    ctx.storage.set("current_time", current_time + 10)
    
    for request_id in list(active_requests.keys()):
        eval_time = ctx.storage.get(f"eval_time_{request_id}", 0)
        if current_time >= eval_time:
            await evaluate_quotes(ctx, request_id)

if __name__ == "__main__":
    agent.run()
