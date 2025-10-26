# agents/coordination_agent.py
import os
import json
import asyncio
import time
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from uagents import Agent, Context
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.aid_protocol import (
    AidProtocol, QuoteRequest, QuoteResponse, Accept, AllocationNotice, Item, Geo
)

# ---------- telemetry helper ----------
import httpx
TELEMETRY_URL = os.getenv("TELEMETRY_URL", "http://127.0.0.1:8088/ingest")

async def emit(ev: dict):
    try:
        async with httpx.AsyncClient(timeout=2) as c:
            await c.post(TELEMETRY_URL, json=ev)
    except Exception:
        pass

# ---------- config ----------
COORDINATOR_NAME = os.getenv("COORDINATOR_NAME", "coordination_agent_1")
COORDINATOR_SEED = os.getenv("COORDINATOR_SEED", "coordination_agent_1_demo_seed")
COORDINATOR_PORT = int(os.getenv("COORDINATOR_PORT", "8002"))

# Claude service endpoint
CLAUDE_SERVICE_URL = os.getenv("CLAUDE_SERVICE_URL", "http://localhost:3000")

# Agent addresses (will be discovered dynamically)
NEED_AGENT_ADDRESSES = [a.strip() for a in os.getenv("NEED_AGENT_ADDRS", "").split(",") if a.strip()]
SUPPLY_AGENT_ADDRESSES = [a.strip() for a in os.getenv("SUPPLY_AGENT_ADDRS", "").split(",") if a.strip()]

# Default agent addresses for testing
DEFAULT_NEED_AGENT = "agent1qgw06us8yrrmnx40dq7vlm5vqyd25tv3qx3kyax9x5k2kz7kuguxjy4a8hu"
DEFAULT_SUPPLY_AGENT_1 = "agent1q0teepydaltv70mnht98uwcxz6murcysrm782k4qge58pap4w6vaqhea6y9"
DEFAULT_SUPPLY_AGENT_2 = "agent1q0teepydaltv70mnht98uwcxz6murcysrm782k4qge58pap4w6vaqhea6y9"

# ---------- data structures ----------
@dataclass
class DisasterRequest:
    request_id: str
    items: List[str]
    quantity_needed: str
    location: str
    priority: str
    contact: Optional[str] = None
    victim_count: Optional[int] = None
    coordinates: Optional[Dict[str, float]] = None
    timestamp: str = ""
    status: str = "pending"

@dataclass
class AgentStatus:
    agent_id: str
    agent_type: str  # "need" or "supply"
    address: str
    status: str  # "active", "busy", "offline"
    last_seen: float
    capabilities: List[str]

# ---------- agent setup ----------
# Configure endpoint so other agents can send messages back
COORDINATOR_ENDPOINT = [f"http://127.0.0.1:{COORDINATOR_PORT}/submit"]
agent = Agent(name=COORDINATOR_NAME, seed=COORDINATOR_SEED, port=COORDINATOR_PORT, endpoint=COORDINATOR_ENDPOINT)

# ---------- state management ----------
active_requests: Dict[str, DisasterRequest] = {}
agent_registry: Dict[str, AgentStatus] = {}
request_assignments: Dict[str, str] = {}  # request_id -> agent_id

# ---------- lifecycle ----------
@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"[{COORDINATOR_NAME}] Address: {agent.address}")
    ctx.logger.info("Coordination Agent started - monitoring Claude service")
    ctx.logger.info(f"NEED_AGENT_ADDRS: {NEED_AGENT_ADDRESSES}")
    ctx.logger.info(f"SUPPLY_AGENT_ADDRS: {SUPPLY_AGENT_ADDRESSES}")
    
    # Start monitoring Claude service for new requests
    asyncio.create_task(monitor_claude_service(ctx))
    
    # Start agent discovery
    asyncio.create_task(discover_agents(ctx))
    
    ctx.logger.info("Background tasks started")

async def monitor_claude_service(ctx: Context):
    """Poll Claude service for new disaster requests"""
    ctx.logger.info("Starting Claude service monitoring loop")
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Get pending requests from Claude service
                response = await client.get(f"{CLAUDE_SERVICE_URL}/api/uagent/pending-requests")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("requests"):
                        ctx.logger.info(f"Found {len(data['requests'])} pending request(s)")
                        for req_data in data["requests"]:
                            await process_new_request(ctx, req_data)
                    else:
                        ctx.logger.debug("No pending requests")
                
                # Get agent updates
                updates_response = await client.get(f"{CLAUDE_SERVICE_URL}/api/uagent/updates")
                if updates_response.status_code == 200:
                    updates_data = updates_response.json()
                    if updates_data.get("success") and updates_data.get("updates"):
                        for update in updates_data["updates"]:
                            await process_agent_update(ctx, update)
                            
        except Exception as e:
            ctx.logger.error(f"Error monitoring Claude service: {e}")
        
        await asyncio.sleep(10)  # Poll every 10 seconds

async def discover_agents(ctx: Context):
    """Discover and register available agents"""
    ctx.logger.info("Starting agent discovery")
    first_run = True
    while True:
        try:
            # In a real implementation, this would use agent discovery protocols
            # For now, we'll use environment variables and direct communication
            
            # Register known need agents
            for addr in NEED_AGENT_ADDRESSES:
                if addr not in agent_registry:
                    agent_registry[addr] = AgentStatus(
                        agent_id=f"need_{len(agent_registry)}",
                        agent_type="need",
                        address=addr,
                        status="active",
                        last_seen=time.time(),
                        capabilities=["disaster_assessment", "priority_evaluation"]
                    )
                    ctx.logger.info(f"Registered need agent: {addr[:30]}...")
            
            # Register known supply agents
            for addr in SUPPLY_AGENT_ADDRESSES:
                if addr not in agent_registry:
                    agent_registry[addr] = AgentStatus(
                        agent_id=f"supply_{len(agent_registry)}",
                        agent_type="supply",
                        address=addr,
                        status="active",
                        last_seen=time.time(),
                        capabilities=["inventory_management", "logistics_coordination"]
                    )
                    ctx.logger.info(f"Registered supply agent: {addr[:30]}...")
            
            if first_run:
                ctx.logger.info(f"Agent registry initialized: {len(agent_registry)} agents")
                first_run = False
                    
        except Exception as e:
            ctx.logger.error(f"Error in agent discovery: {e}")
        
        await asyncio.sleep(30)  # Check every 30 seconds

async def process_new_request(ctx: Context, req_data: Dict[str, Any]):
    """Process a new disaster request from Claude service"""
    request_id = req_data.get("request_id")
    
    if request_id in active_requests:
        return  # Already processed
    
    # Create disaster request object
    disaster_req = DisasterRequest(
        request_id=request_id,
        items=req_data.get("items", []),
        quantity_needed=req_data.get("quantity", "unknown"),
        location=req_data.get("location", {}).get("address", "unknown"),
        priority=req_data.get("priority", "medium"),
        contact=req_data.get("contact"),
        victim_count=req_data.get("victim_count", 0),
        coordinates=req_data.get("location", {}).get("coordinates"),
        timestamp=req_data.get("timestamp", ""),
        status="pending"
    )
    
    active_requests[request_id] = disaster_req
    
    ctx.logger.info(f"New disaster request: {request_id}")
    ctx.logger.info(f"  Items: {disaster_req.items}")
    ctx.logger.info(f"  Location: {disaster_req.location}")
    ctx.logger.info(f"  Priority: {disaster_req.priority}")
    
    # Assign to appropriate agents
    await assign_request_to_agents(ctx, disaster_req)
    
    # Emit telemetry
    await emit({
        "ts": time.time(),
        "agent_type": "coordinator",
        "agent_id": COORDINATOR_NAME,
        "event_type": "request_received",
        "request_id": request_id,
        "priority": disaster_req.priority,
        "items_count": len(disaster_req.items)
    })

async def assign_request_to_agents(ctx: Context, disaster_req: DisasterRequest):
    """Assign disaster request to appropriate need and supply agents"""
    
    ctx.logger.info(f"Assigning request {disaster_req.request_id} to agents")
    ctx.logger.info(f"Agent registry size: {len(agent_registry)}")
    
    # Find available need agents
    need_agents = [agent for agent in agent_registry.values() 
                   if agent.agent_type == "need" and agent.status == "active"]
    
    # Find available supply agents
    supply_agents = [agent for agent in agent_registry.values() 
                     if agent.agent_type == "supply" and agent.status == "active"]
    
    ctx.logger.info(f"Found {len(need_agents)} need agents, {len(supply_agents)} supply agents")
    
    if not need_agents or not supply_agents:
        ctx.logger.warning(f"No available agents for request {disaster_req.request_id}")
        ctx.logger.warning(f"Need agents: {len(need_agents)}, Supply agents: {len(supply_agents)}")
        return
    
    # Create quote request for need agents
    if disaster_req.coordinates:
        geo = Geo(
            lat=disaster_req.coordinates["latitude"],
            lon=disaster_req.coordinates["longitude"],
            label=disaster_req.location
        )
    else:
        # Default coordinates if not available
        geo = Geo(lat=37.8715, lon=-122.2730, label=disaster_req.location)
    
    # Convert items to Item objects
    items = []
    for item_name in disaster_req.items:
        items.append(Item(
            name=item_name,
            qty=1,  # Default quantity, should be parsed from quantity_needed
            unit="ea"
        ))
    
    quote_req = QuoteRequest(
        need_id=disaster_req.request_id,
        location=geo,
        items=items,
        priority=disaster_req.priority,
        max_eta_hours=24.0  # Default max ETA
    )
    
    # Send to need agents
    for need_agent in need_agents:
        try:
            await ctx.send(need_agent.address, quote_req)
            ctx.logger.info(f"Sent quote request to need agent: {need_agent.agent_id}")
        except Exception as e:
            ctx.logger.error(f"Failed to send to need agent {need_agent.agent_id}: {e}")
    
    # Send to supply agents
    for supply_agent in supply_agents:
        try:
            await ctx.send(supply_agent.address, quote_req)
            ctx.logger.info(f"Sent quote request to supply agent: {supply_agent.agent_id}")
        except Exception as e:
            ctx.logger.error(f"Failed to send to supply agent {supply_agent.agent_id}: {e}")
    
    # Mark as assigned
    request_assignments[disaster_req.request_id] = "assigned"
    disaster_req.status = "processing"

async def process_agent_update(ctx: Context, update: Dict[str, Any]):
    """Process updates from agents"""
    request_id = update.get("request_id")
    agent_id = update.get("agent_id")
    status = update.get("status")
    
    if request_id in active_requests:
        active_requests[request_id].status = status
        ctx.logger.info(f"Request {request_id} status updated to: {status}")
        
        # Emit telemetry
        await emit({
            "ts": time.time(),
            "agent_type": "coordinator",
            "agent_id": COORDINATOR_NAME,
            "event_type": "status_update",
            "request_id": request_id,
            "agent_id": agent_id,
            "status": status
        })

# ---------- protocol handlers ----------
@AidProtocol.on_message(model=QuoteResponse)
async def on_quote_response(ctx: Context, sender: str, resp: QuoteResponse):
    """Handle quote responses from agents"""
    ctx.logger.info(f"Quote response from {sender}: {resp.supplier_id}")
    ctx.logger.info(f"  Cost: ${resp.total_cost}, ETA: {resp.eta_hours}h")
    ctx.logger.info(f"  Coverage: {resp.coverage_ratio}")
    
    # Emit telemetry
    await emit({
        "ts": time.time(),
        "agent_type": "coordinator",
        "agent_id": COORDINATOR_NAME,
        "event_type": "quote_received",
        "request_id": resp.need_id,
        "supplier_id": resp.supplier_id,
        "cost": resp.total_cost,
        "eta_hours": resp.eta_hours,
        "coverage": resp.coverage_ratio
    })

@AidProtocol.on_message(model=AllocationNotice)
async def on_allocation_notice(ctx: Context, sender: str, notice: AllocationNotice):
    """Handle allocation confirmations"""
    ctx.logger.info(f"Allocation confirmed by {notice.supplier_id}")
    ctx.logger.info(f"  Items: {[f'{i.name}:{i.qty}' for i in notice.items]}")
    
    # Update request status
    if notice.need_id in active_requests:
        active_requests[notice.need_id].status = "allocated"
    
    # Emit telemetry
    await emit({
        "ts": time.time(),
        "agent_type": "coordinator",
        "agent_id": COORDINATOR_NAME,
        "event_type": "allocation_confirmed",
        "request_id": notice.need_id,
        "supplier_id": notice.supplier_id,
        "items": [{"name": i.name, "qty": i.qty} for i in notice.items]
    })

# ---------- status endpoints ----------
# Remove the problematic message handler for now
# The coordination agent will work without this endpoint

# Include the protocol
agent.include(AidProtocol)

if __name__ == "__main__":
    agent.run()
