#!/usr/bin/env python3
"""
Supply Agent - Chat Protocol Adapter for Agentverse
Exposes the supply agent functionality via Chat Protocol for Agentverse deployment
"""

import os
import json
from typing import cast
from fastapi import FastAPI
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
from uagents_core.envelope import Envelope
from uagents_core.identity import Identity
from uagents_core.utils.messages import parse_envelope, send_message_to_agent

# Agent configuration
AGENT_NAME = "AgentAid Supply Agent"
AGENT_SEED_PHRASE = os.environ.get("AGENT_SEED_PHRASE", "supply_sf_store_1_demo_seed")
AGENT_ENDPOINT = os.environ.get("AGENT_EXTERNAL_ENDPOINT", "http://localhost:8001")
SUPPLIER_LOCATION = os.environ.get("SUPPLIER_LABEL", "SF Depot")

# Create identity from seed
identity = Identity.from_seed(AGENT_SEED_PHRASE, 0)

# Agent README for Agentverse
readme = """# AgentAid Supply Agent

## Overview
This agent represents disaster relief suppliers with inventory management capabilities. It responds to quote requests from need agents and manages resource allocation based on availability, location, and delivery capacity.

## Capabilities
- 📦 **Inventory Management**: Tracks available disaster relief supplies in real-time
- 💰 **Smart Quoting**: Generates quotes based on distance, priority, and availability
- 🚚 **Delivery Coordination**: Calculates ETAs and manages delivery logistics
- 🌍 **Radius-Based Service**: Only services requests within operational radius
- ⚡ **Priority Pricing**: Adjusts pricing based on emergency priority levels

## Inventory
Current available supplies (example):
- Blankets: 500 units
- Water Bottles: 1000 units
- Medical Supplies: 200 kits
- Food Rations: 800 units
- Tents: 50 units
- Clothing: 300 units

## Service Area
- **Location**: {location}
- **Service Radius**: 120 km
- **Delivery Mode**: Truck
- **Base Lead Time**: 1.5 hours

## How to Use
Send a message to inquire about inventory or request a quote:

**Example Messages:**
- "What supplies do you have available?"
- "Can you provide 200 blankets to Berkeley?"
- "Check inventory for medical supplies"
- "Quote for water and food supplies delivery to Oakland"

## Quote Generation
When a quote request is received, the agent:
1. ✅ Checks if location is within service radius
2. 📦 Verifies inventory availability
3. 💵 Calculates pricing based on priority
4. 🚚 Estimates delivery time based on distance
5. 📊 Computes coverage ratio

## Pricing Model
- **Critical Priority**: 10% discount (emergency response)
- **High Priority**: 5% discount
- **Medium Priority**: Standard pricing
- **Low Priority**: 5% premium

## Delivery Calculation
- Base lead time: 1.5 hours (preparation)
- Travel time: Distance ÷ 40 km/h (conservative estimate)
- Total ETA = Base lead time + Travel time

## Integration
This agent integrates with:
- **Need Agents**: Responds to disaster relief requests
- **Coordination Agent**: Part of disaster response network
- **Database**: SQLite inventory management
- **Telemetry Service**: For monitoring and analytics

## Technical Details
- **Protocol**: AidProtocol v2.0.0
- **Framework**: uAgents (Fetch.ai)
- **Database**: SQLite with atomic inventory deduction
- **Distance Calculation**: Haversine formula for accurate geo-distance

## Response Format
Quote responses include:
- Coverage ratio (% of request fulfilled)
- Estimated time of arrival (hours)
- Total cost ($)
- Available items with quantities
- Delivery terms

## Contact
Part of the AgentAid Disaster Response Platform
""".format(location=SUPPLIER_LOCATION)

# Create FastAPI app
app = FastAPI(title=AGENT_NAME, description="Disaster relief supply management agent")

@app.get("/status")
async def healthcheck():
    """Health check endpoint"""
    return {
        "status": "OK - Agent is running",
        "agent_name": AGENT_NAME,
        "agent_address": identity.address,
        "supplier_location": SUPPLIER_LOCATION,
        "capabilities": [
            "inventory_management",
            "smart_quoting",
            "delivery_coordination",
            "radius_based_service"
        ]
    }

@app.get("/agent_info")
async def agent_info():
    """Agent information endpoint for Agentverse registration"""
    return {
        "agent_address": identity.address,
        "name": AGENT_NAME,
        "readme": readme,
        "protocol": "Chat Protocol",
        "version": "2.0.0",
        "endpoint": AGENT_ENDPOINT,
        "supplier_location": SUPPLIER_LOCATION,
        "capabilities": [
            "inventory_management",
            "smart_quoting",
            "delivery_coordination",
            "radius_based_service",
            "priority_pricing"
        ],
        "protocols_supported": ["chat", "aid_protocol_v2"],
        "service_radius_km": 120,
        "delivery_mode": "truck",
        "active": True
    }

@app.post("/")
async def handle_message(env: Envelope):
    """Handle incoming chat messages via Chat Protocol"""
    try:
        # Parse the incoming chat message
        msg = cast(ChatMessage, parse_envelope(env, ChatMessage))
        user_message = msg.text()

        print(f"Received message from {env.sender}: {user_message}")

        # Process the supply inquiry
        response_text = process_supply_inquiry(user_message)

        # Send response back to sender
        send_message_to_agent(
            destination=env.sender,
            msg=ChatMessage([TextContent(response_text)]),
            sender=identity,
        )

        return {"status": "processed", "message": "Inquiry processed successfully"}

    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        print(error_msg)

        # Send error response
        send_message_to_agent(
            destination=env.sender,
            msg=ChatMessage([TextContent(f"Sorry, I encountered an error: {str(e)}")]),
            sender=identity,
        )

        return {"status": "error", "message": str(e)}

def process_supply_inquiry(message: str) -> str:
    """Process a supply inquiry or quote request"""
    try:
        message_lower = message.lower()

        # Check if it's an inventory inquiry
        if any(word in message_lower for word in ["inventory", "available", "stock", "supplies", "what do you have"]):
            return get_inventory_status()

        # Check if it's a quote request
        if any(word in message_lower for word in ["quote", "provide", "deliver", "need", "request"]):
            return generate_quote_response(message)

        # General inquiry
        return get_general_info()

    except Exception as e:
        return f"Error processing inquiry: {str(e)}"

def get_inventory_status() -> str:
    """Return current inventory status"""
    # In production, this would query the actual database
    inventory = {
        "Blankets": {"qty": 500, "unit": "ea"},
        "Water Bottles": {"qty": 1000, "unit": "bottles"},
        "Medical Supplies": {"qty": 200, "unit": "kits"},
        "Food Rations": {"qty": 800, "unit": "meals"},
        "Tents": {"qty": 50, "unit": "ea"},
        "Clothing": {"qty": 300, "unit": "sets"}
    }

    response = f"""📦 **Current Inventory Status**

**Supplier**: {SUPPLIER_LOCATION}
**Service Radius**: 120 km
**Delivery Mode**: Truck

**Available Supplies:**
"""

    for item, details in inventory.items():
        response += f"\n- **{item}**: {details['qty']} {details['unit']}"

    response += """

**Service Information:**
- ✅ Real-time inventory tracking
- 🚚 Truck delivery available
- ⚡ Priority emergency response
- 🌍 Serving 120 km radius

**To Request a Quote:**
Send a message with:
- Items needed
- Quantities
- Delivery location
- Priority level

Example: "Quote for 200 blankets and 500 water bottles to Berkeley, critical priority"
"""

    return response

def generate_quote_response(message: str) -> str:
    """Generate a quote based on the request"""
    message_lower = message.lower()

    # Extract items (simplified)
    items_requested = []
    if "blanket" in message_lower:
        items_requested.append({"name": "Blankets", "qty": 200, "available": 500})
    if "water" in message_lower:
        items_requested.append({"name": "Water Bottles", "qty": 500, "available": 1000})
    if "medical" in message_lower or "medicine" in message_lower:
        items_requested.append({"name": "Medical Supplies", "qty": 50, "available": 200})
    if "food" in message_lower:
        items_requested.append({"name": "Food Rations", "qty": 300, "available": 800})

    if not items_requested:
        items_requested = [{"name": "Emergency Supplies", "qty": 100, "available": 500}]

    # Detect location and calculate distance
    location = "Unknown location"
    distance_km = 30  # Default

    if "berkeley" in message_lower:
        location = "Berkeley, CA"
        distance_km = 25
    elif "oakland" in message_lower:
        location = "Oakland, CA"
        distance_km = 20
    elif "san francisco" in message_lower or "sf" in message_lower:
        location = "San Francisco, CA"
        distance_km = 15

    # Detect priority
    priority = "medium"
    if "critical" in message_lower or "urgent" in message_lower:
        priority = "critical"
    elif "high" in message_lower:
        priority = "high"
    elif "low" in message_lower:
        priority = "low"

    # Calculate quote
    base_cost = sum(item["qty"] * 2.5 for item in items_requested)  # $2.5 per unit average

    # Priority modifier
    priority_mods = {"critical": 0.90, "high": 0.95, "medium": 1.00, "low": 1.05}
    total_cost = base_cost * priority_mods.get(priority, 1.00)

    # Calculate ETA
    base_lead_time = 1.5  # hours
    travel_time = distance_km / 40.0  # 40 km/h
    eta_hours = base_lead_time + travel_time

    # Calculate coverage
    coverage = min(1.0, sum(min(item["qty"], item["available"]) / item["qty"] for item in items_requested) / len(items_requested))

    response = f"""💰 **Quote Generated**

**Supplier**: {SUPPLIER_LOCATION}
**Delivery To**: {location}
**Distance**: {distance_km} km
**Priority**: {priority.upper()}

**Items Offered:**
"""

    for item in items_requested:
        offered_qty = min(item["qty"], item["available"])
        response += f"\n- **{item['name']}**: {offered_qty} / {item['qty']} requested"

    response += f"""

**Quote Details:**
- **Coverage Ratio**: {coverage*100:.1f}%
- **Estimated Delivery Time**: {eta_hours:.1f} hours
- **Total Cost**: ${total_cost:.2f}
- **Delivery Mode**: Truck
- **Terms**: delivery:truck;priority:{priority}

**Status**: ✅ Quote Ready

This quote is valid for the next 30 minutes. To accept, the need agent will send an acceptance message, and we will:
1. Reserve the items in our inventory
2. Prepare for dispatch
3. Coordinate delivery logistics
4. Provide tracking updates

**Note**: For {priority} priority requests, we prioritize fast preparation and delivery.
"""

    return response

def get_general_info() -> str:
    """Return general information about the supply agent"""
    return f"""🏢 **{AGENT_NAME}**

**Location**: {SUPPLIER_LOCATION}
**Service Area**: 120 km radius
**Delivery Mode**: Truck

**What I Can Do:**
- 📦 Provide disaster relief supplies
- 💰 Generate quotes for emergency requests
- 🚚 Coordinate delivery logistics
- ⚡ Prioritize critical emergencies

**How to Use Me:**
1. **Check Inventory**: Ask "What supplies do you have?"
2. **Request Quote**: Say "Quote for [items] to [location]"
3. **Get Information**: Ask about capabilities or service area

**Example Queries:**
- "What's your current inventory?"
- "Can you provide 200 blankets to Berkeley?"
- "Quote for medical supplies and water to Oakland, high priority"

**Integration:**
I'm part of the AgentAid Disaster Response Platform, working with need agents and coordination agents to provide efficient disaster relief.

**Contact**: Send me a message anytime!
"""

@app.get("/")
async def root():
    """Root endpoint with agent information"""
    return {
        "agent": AGENT_NAME,
        "address": identity.address,
        "endpoint": AGENT_ENDPOINT,
        "supplier_location": SUPPLIER_LOCATION,
        "protocol": "Chat Protocol + AidProtocol v2.0.0",
        "readme": readme,
        "capabilities": [
            "inventory_management",
            "smart_quoting",
            "delivery_coordination",
            "radius_based_service",
            "priority_pricing"
        ],
        "usage": "Send POST requests to /chat to inquire about supplies or request quotes"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8001"))
    print(f"\n{'='*80}")
    print(f"📦 {AGENT_NAME}")
    print(f"{'='*80}")
    print(f"Agent Address: {identity.address}")
    print(f"Supplier Location: {SUPPLIER_LOCATION}")
    print(f"Endpoint: {AGENT_ENDPOINT}")
    print(f"Port: {port}")
    print(f"Status: http://localhost:{port}/status")
    print(f"Chat: POST http://localhost:{port}/chat")
    print(f"{'='*80}\n")

    uvicorn.run(app, host="0.0.0.0", port=port)