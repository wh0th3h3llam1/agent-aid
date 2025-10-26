#!/usr/bin/env python3
"""
Supply Agent - Fixed Version with Auto-Response
Automatically responds to quote requests from need agents
"""

import os
import json
import re
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

# Mock inventory (pre-loaded data)
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

# Location data for distance calculation
SUPPLIER_COORDS = {"lat": 37.78, "lon": -122.42}  # San Francisco

LOCATION_COORDS = {
    "berkeley": {"lat": 37.8715, "lon": -122.2730, "distance_km": 25},
    "oakland": {"lat": 37.8044, "lon": -122.2712, "distance_km": 20},
    "san francisco": {"lat": 37.78, "lon": -122.42, "distance_km": 5},
    "sf": {"lat": 37.78, "lon": -122.42, "distance_km": 5}
}

# Create FastAPI app
app = FastAPI(title=AGENT_NAME, description="Disaster relief supply management agent")

@app.get("/status")
async def healthcheck():
    """Health check endpoint"""
    total_items = sum(item["available"] for item in INVENTORY.values())
    return {
        "status": "OK - Agent is running",
        "agent_name": AGENT_NAME,
        "agent_address": identity.address,
        "supplier_location": SUPPLIER_LOCATION,
        "inventory_items": len(INVENTORY),
        "total_units": total_items
    }

@app.post("/")
async def handle_message(env: Envelope):
    """Handle incoming chat messages via Chat Protocol"""
    try:
        # Parse the incoming chat message
        msg = cast(ChatMessage, parse_envelope(env, ChatMessage))
        user_message = msg.text()

        print(f"\n{'='*80}")
        print(f"📨 Received message from {env.sender[:20]}...")
        print(f"Message: {user_message[:100]}...")
        print(f"{'='*80}")

        # Check if this is a quote request
        if "QUOTE_REQUEST" in user_message:
            # This is a quote request from need agent
            response_text = await process_quote_request(user_message, env.sender)
        else:
            # General inquiry
            response_text = process_general_inquiry(user_message)

        # Send response back to sender
        send_message_to_agent(
            destination=env.sender,
            msg=ChatMessage([TextContent(response_text)]),
            sender=identity,
        )

        return {"status": "processed"}

    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": str(e)}

async def process_quote_request(message: str, need_agent_address: str) -> str:
    """Process a quote request from need agent"""
    try:
        print(f"\n💰 Processing quote request...")
        
        # Extract request ID
        req_id_match = re.search(r'QUOTE_REQUEST:(\S+)', message)
        request_id = req_id_match.group(1) if req_id_match else "UNKNOWN"
        
        # Extract items
        items_match = re.search(r'Items:\s*([^\n]+)', message, re.IGNORECASE)
        items_str = items_match.group(1).strip() if items_match else ""
        items = [item.strip().lower() for item in items_str.split(',')]
        
        # Extract quantity
        qty_match = re.search(r'Quantity:\s*(\d+)', message, re.IGNORECASE)
        requested_qty = int(qty_match.group(1)) if qty_match else 0
        
        # Extract location
        loc_match = re.search(r'Location:\s*([^\n]+)', message, re.IGNORECASE)
        location = loc_match.group(1).strip() if loc_match else "Unknown"
        
        # Extract priority
        priority_match = re.search(r'Priority:\s*(\w+)', message, re.IGNORECASE)
        priority = priority_match.group(1).lower() if priority_match else "medium"
        
        print(f"   Request ID: {request_id}")
        print(f"   Items: {items}")
        print(f"   Quantity: {requested_qty}")
        print(f"   Location: {location}")
        print(f"   Priority: {priority}")
        
        # Check inventory and generate quote
        quote = generate_quote(items, requested_qty, location, priority)
        
        # Format response
        response = f"""QUOTE_RESPONSE:{request_id}

**Supplier**: {SUPPLIER_LOCATION}
**Items**: {', '.join(items)}
**Quantity**: {quote['quantity_offered']}
**ETA**: {quote['eta_hours']} hours
**Coverage**: {quote['coverage_pct']:.1f}%
**Delivery To**: {location}

**Details**:
- Available from inventory: {quote['quantity_offered']} units
- Delivery time: {quote['eta_hours']} hours
- Distance: {quote['distance_km']} km
- Priority: {priority}

Status: ✅ Quote ready for evaluation"""

        print(f"\n✅ Quote generated:")
        print(f"   Quantity: {quote['quantity_offered']}")
        print(f"   ETA: {quote['eta_hours']} hours")
        print(f"   Coverage: {quote['coverage_pct']:.1f}%")
        
        return response

    except Exception as e:
        print(f"❌ Error generating quote: {e}")
        return f"Error generating quote: {str(e)}"

def generate_quote(items: list, requested_qty: int, location: str, priority: str) -> dict:
    """Generate a quote based on inventory and location"""
    
    # Find matching items in inventory
    available_qty = 0
    for item in items:
        for inv_item, inv_data in INVENTORY.items():
            if item in inv_item or inv_item in item:
                available_qty = max(available_qty, inv_data["available"])
                break
    
    # Determine how much we can offer
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
    eta_hours = round(base_lead_time + travel_time, 1)
    
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
        "coverage_pct": coverage_pct,
        "priority": priority
    }

def process_supply_inquiry(message: str) -> str:
    """Process a supply inquiry or quote request"""
    try:
        message_lower = message.lower()

        # Check if it's a quote request FIRST (highest priority)
        if any(word in message_lower for word in ["quote_request", "quote", "quantity:", "priority:", "items:"]):
            print(f"🔍 Detected quote request")
            # Parse the message and generate quote
            import re
            items_match = re.search(r'Items:\s*([^\n]+)', message, re.IGNORECASE)
            qty_match = re.search(r'Quantity:\s*(\d+)', message, re.IGNORECASE)
            loc_match = re.search(r'Location:\s*([^\n]+)', message, re.IGNORECASE)
            priority_match = re.search(r'Priority:\s*(\w+)', message, re.IGNORECASE)
            req_id_match = re.search(r'QUOTE_REQUEST:(\S+)', message)
            
            items = [items_match.group(1).strip()] if items_match else ["emergency supplies"]
            quantity = int(qty_match.group(1)) if qty_match else 50
            location = loc_match.group(1).strip() if loc_match else "Unknown"
            priority = priority_match.group(1).strip() if priority_match else "medium"
            request_id = req_id_match.group(1) if req_id_match else "UNKNOWN"
            
            # Generate quote
            quote = generate_quote(items, quantity, location, priority)
            
            # Format response
            response = f"""QUOTE_RESPONSE:{request_id}

**Supplier**: {SUPPLIER_LOCATION}
**Items**: {', '.join(items)}
**Quantity**: {quote['quantity_offered']}
**ETA**: {quote['eta_hours']} hours
**Coverage**: {quote['coverage_pct']:.1f}%
**Delivery To**: {location}

**Details**:
- Available from inventory: {quote['quantity_offered']} units
- Delivery time: {quote['eta_hours']} hours
- Distance: {quote['distance_km']} km
- Priority: {priority}

Status: ✅ Quote ready"""
            
            return response

        # Check if it's an inventory inquiry
        if any(word in message_lower for word in ["inventory", "available", "stock", "what do you have"]):
            print(f"🔍 Detected inventory inquiry")
            return get_inventory_status()

        # General inquiry
        print(f"🔍 General inquiry")
        return get_general_info()

    except Exception as e:
        return f"Error processing inquiry: {str(e)}"

def process_general_inquiry(message: str) -> str:
    """Process general inquiries about inventory"""
    return process_supply_inquiry(message)

def get_inventory_status() -> str:
    """Return current inventory status"""
    response = f"""📦 **Current Inventory Status**

**Supplier**: {SUPPLIER_LOCATION}
**Location**: San Francisco, CA
**Service Radius**: 120 km

**Available Supplies:**
"""
    
    for item, details in INVENTORY.items():
        response += f"\n- **{item.title()}**: {details['available']} {details['unit']}"
    
    response += """

**Service Information:**
- ✅ Real-time inventory tracking
- 🚚 Truck delivery available
- ⚡ Priority emergency response
- 🌍 Serving Bay Area (120 km radius)

Send a quote request to get delivery estimates!"""
    
    return response

def get_general_info() -> str:
    """Return general information"""
    return f"""🏢 **{AGENT_NAME}**

**Location**: {SUPPLIER_LOCATION}
**Service Area**: 120 km radius
**Inventory Items**: {len(INVENTORY)}

**Capabilities:**
- 📦 Disaster relief supplies
- 💰 Automatic quote generation
- 🚚 Fast delivery coordination
- ⚡ Priority emergency response

**How to Use:**
- Ask "What supplies do you have?"
- Need agents can send quote requests automatically

**Status**: ✅ Online and ready to serve!"""

@app.post("/simple")
async def handle_simple_message(request: dict):
    """Handle simple HTTP messages (not uAgents protocol)"""
    try:
        message = request.get("message", "")
        sender = request.get("sender", "unknown")
        
        print(f"\n📨 Simple HTTP message from {sender}")
        print(f"Message: {message[:100]}...")
        
        # Process the supply inquiry
        response_text = process_supply_inquiry(message)
        
        # Send response back to need agent via HTTP
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    "http://localhost:8000/quote_response",
                    json={"message": response_text, "sender": identity.address},
                    timeout=5.0
                )
                print(f"✅ Quote response sent back to need agent!")
            except Exception as e:
                print(f"⚠️  Could not send response back: {e}")
        
        return {"status": "processed", "message": "Quote generated and sent"}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}

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
    print(f"📦 {AGENT_NAME} - FIXED VERSION")
    print(f"{'='*80}")
    print(f"Agent Address: {identity.address}")
    print(f"Supplier Location: {SUPPLIER_LOCATION}")
    print(f"Endpoint: {AGENT_ENDPOINT}")
    print(f"Port: {port}")
    print(f"Inventory Items: {len(INVENTORY)}")
    print(f"Total Units: {sum(item['available'] for item in INVENTORY.values())}")
    print(f"{'='*80}\n")

    uvicorn.run(app, host="0.0.0.0", port=port)
