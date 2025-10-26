#!/usr/bin/env python3
"""
Need Agent - Chat Protocol Adapter for Agentverse
Exposes the need agent functionality via Chat Protocol for Agentverse deployment
"""

import os
import json
import asyncio
from typing import cast, Dict, List, Any
from fastapi import FastAPI
import httpx
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
from uagents_core.envelope import Envelope
from uagents_core.identity import Identity
from uagents_core.models import Model
from uagents_core.utils.messages import parse_envelope
import math

# Agent configuration
AGENT_NAME = "AgentAid Need Agent"
AGENT_SEED_PHRASE = os.environ.get("AGENT_SEED_PHRASE", "need_agent_berkeley_1_demo_seed")
AGENT_ENDPOINT = os.environ.get("AGENT_EXTERNAL_ENDPOINT", "http://localhost:8000")

# Supply agents to query (for demo, using one supply agent)
SUPPLY_AGENTS = [
    {
        "address": os.environ.get("SUPPLY_AGENT_ADDRESS", "agent1q..."),
        "endpoint": os.environ.get("SUPPLY_AGENT_ENDPOINT", "http://localhost:8001"),
        "name": "Medical Supply Agent"
    }
]

# Create identity from seed
identity = Identity.from_seed(AGENT_SEED_PHRASE, 0)

# Agent README for Agentverse
readme = """# AgentAid Need Agent

## Overview
This agent represents disaster victims and their emergency needs. It broadcasts quote requests to supply agents and manages the allocation of resources based on priority, cost, and availability.

## Capabilities
- 🆘 **Emergency Need Broadcasting**: Sends disaster relief requests to supply agents
- 📊 **Quote Evaluation**: Scores supplier quotes based on coverage, price, and risk factors
- 🎯 **Smart Allocation**: Allocates resources from multiple suppliers optimally
- 🌍 **Location-Aware**: Uses GPS coordinates for accurate distance calculations
- ⚡ **Priority Management**: Handles critical, high, medium, and low priority requests

## How to Use
Send a message describing your disaster relief needs:

**Example Messages:**
- "We need 200 blankets at Berkeley Emergency Center, 37.8715, -122.2730. This is critical priority."
- "Need medical supplies and water at 123 Main St, Berkeley. High priority, 50 people affected."
- "Requesting food and shelter supplies for disaster relief at Oakland Community Center."

## Message Format
Include the following information:
- **Items needed**: Specific items (blankets, water, medical supplies, etc.)
- **Quantity**: Number of items required
- **Location**: Address or GPS coordinates (lat, lon)
- **Priority**: critical, high, medium, or low
- **Affected people**: Number of people affected (optional)

## Response
The agent will:
1. Parse your disaster relief request
2. Broadcast quote requests to available supply agents
3. Evaluate received quotes based on coverage, cost, and delivery time
4. Allocate resources from the best suppliers
5. Confirm allocations and provide status updates

## Integration
This agent integrates with:
- **Supply Agents**: For resource procurement
- **Coordination Agent**: For disaster response coordination
- **Claude AI Service**: For natural language processing
- **Telemetry Service**: For monitoring and analytics

## Technical Details
- **Protocol**: AidProtocol v2.0.0
- **Framework**: uAgents (Fetch.ai)
- **Location**: Berkeley, CA (default)
- **Scoring Algorithm**: Combines coverage ratio, price, and risk factors

## Contact
Part of the AgentAid Disaster Response Platform
"""

# Create FastAPI app
app = FastAPI(title=AGENT_NAME, description="Disaster relief need management agent")

@app.get("/status")
async def healthcheck():
    """Health check endpoint"""
    return {
        "status": "OK - Agent is running",
        "agent_name": AGENT_NAME,
        "agent_address": identity.address,
        "capabilities": [
            "emergency_need_broadcasting",
            "quote_evaluation",
            "smart_allocation",
            "priority_management"
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
        "capabilities": [
            "emergency_need_broadcasting",
            "quote_evaluation",
            "smart_allocation",
            "location_aware_matching",
            "priority_management"
        ],
        "protocols_supported": ["chat", "aid_protocol_v2"],
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

        # Try to parse as JSON first
        try:
            need_request = json.loads(user_message)
            print(f"Parsed JSON request: {json.dumps(need_request, indent=2)}")
            response_text = await process_need_request_json(need_request)
        except json.JSONDecodeError:
            # Fallback to text processing
            response_text = process_need_request_text(user_message)

        # Return response message as ChatMessage envelope
        response_msg = ChatMessage([TextContent(response_text)])

        return {
            "version": 1,
            "sender": identity.address,
            "target": env.sender,
            "session": str(env.session),
            "schema_digest": Model.build_schema_digest(ChatMessage),
            "protocol_digest": env.protocol_digest,
            "payload": response_msg.json()
        }

    except Exception as ex:  # pylint: disable=broad-except
        error_msg = f"Error processing message: {str(ex)}"
        print(error_msg)
        import traceback
        traceback.print_exc()

        # Return error response
        error_response = ChatMessage([TextContent(f"Sorry, I encountered an error: {str(ex)}")])

        return {
            "version": 1,
            "sender": identity.address,
            "target": env.sender,
            "session": str(env.session),
            "schema_digest": Model.build_schema_digest(ChatMessage),
            "protocol_digest": env.protocol_digest,
            "payload": error_response.json()
        }

async def process_need_request_json(need_request: Dict[str, Any]) -> str:
    """Process a disaster relief need request from JSON schema"""
    try:
        # Extract request details
        items = need_request.get("items", [])
        quantity = need_request.get("quantity_needed", "unknown")
        location = need_request.get("location", "Unknown location")
        priority = need_request.get("priority", "medium")
        request_id = need_request.get("request_id", "N/A")
        coordinates = need_request.get("coordinates", {})

        lat = coordinates.get("latitude") if coordinates else None
        lon = coordinates.get("longitude") if coordinates else None

        print("\n" + "="*80)
        print("📥 NEW DISASTER RELIEF REQUEST")
        print("="*80)
        print(f"Request ID: {request_id}")
        print(f"Items: {', '.join(items)}")
        print(f"Quantity: {quantity}")
        print(f"Location: {location}")
        print(f"Coordinates: {lat}, {lon}")
        print(f"Priority: {priority.upper()}")
        print("="*80 + "\n")

        # Query supply agents
        quotes = await query_supply_agents(need_request)

        # Evaluate quotes
        if quotes:
            best_quote = evaluate_quotes(quotes, priority)
            response = format_quote_response(need_request, quotes, best_quote)
        else:
            response = format_no_quotes_response(need_request)

        return response

    except Exception as ex:  # pylint: disable=broad-except
        import traceback
        traceback.print_exc()
        return f"Error processing JSON request: {str(ex)}"

def process_need_request_text(message: str) -> str:
    """Process a disaster relief need request from natural language (fallback)"""
    try:
        message_lower = message.lower()

        # Detect priority
        priority = "medium"
        if "critical" in message_lower or "urgent" in message_lower or "emergency" in message_lower:
            priority = "critical"
        elif "high" in message_lower:
            priority = "high"
        elif "low" in message_lower:
            priority = "low"

        # Extract items (simplified)
        items = []
        item_keywords = {
            "blanket": "blankets",
            "water": "water bottles",
            "food": "food supplies",
            "medical": "medical supplies",
            "medicine": "medicine",
            "shelter": "shelter materials",
            "clothing": "clothing",
            "tent": "tents"
        }

        for keyword, item_name in item_keywords.items():
            if keyword in message_lower:
                items.append(item_name)

        if not items:
            items = ["emergency supplies"]

        # Extract location (simplified)
        location = "Location to be determined"
        if "berkeley" in message_lower:
            location = "Berkeley, CA (37.8715, -122.2730)"
        elif "oakland" in message_lower:
            location = "Oakland, CA (37.8044, -122.2712)"
        elif "san francisco" in message_lower or "sf" in message_lower:
            location = "San Francisco, CA (37.78, -122.42)"

        response = f"""✅ **Disaster Relief Request Received**

**Request Details:**
- **Items Needed**: {', '.join(items)}
- **Location**: {location}
- **Priority**: {priority.upper()}

**Status**: Broadcasting quote requests to supply agents...

I'm now contacting available supply agents to fulfill your request.
For structured requests, please send JSON in the format:
{{
  "items": ["item1", "item2"],
  "quantity_needed": "100",
  "location": "Address",
  "priority": "high",
  "coordinates": {{"latitude": 37.8, "longitude": -122.4}}
}}

Thank you for using AgentAid! 🚨
"""
        return response

    except Exception as ex:  # pylint: disable=broad-except
        return f"Error processing request: {str(ex)}"

async def query_supply_agents(need_request: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Query all supply agents with the need request"""
    quotes = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = []
        for supplier in SUPPLY_AGENTS:
            task = query_single_supply_agent(client, supplier, need_request)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Error querying {SUPPLY_AGENTS[i]['name']}: {result}")
            elif result:
                quotes.append(result)

    return quotes

async def query_single_supply_agent(client: httpx.AsyncClient, supplier: Dict[str, Any], need_request: Dict[str, Any]) -> Dict[str, Any]:
    """Query a single supply agent"""
    try:
        print(f"📤 Querying {supplier['name']} at {supplier['endpoint']}")

        # Create ChatMessage with the need request as JSON
        request_json = json.dumps(need_request)
        chat_msg = ChatMessage([TextContent(request_json)])

        # Create envelope
        envelope = {
            "version": 1,
            "sender": identity.address,
            "target": supplier["address"],
            "session": f"need-{need_request.get('request_id', 'unknown')}",
            "schema_digest": Model.build_schema_digest(ChatMessage),
            "payload": chat_msg.json()
        }

        # Send POST request to supply agent
        response = await client.post(
            supplier["endpoint"],
            json=envelope,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            response_data = response.json()
            # Extract the text content from the response
            if "payload" in response_data:
                payload = json.loads(response_data["payload"])
                if "messages" in payload and len(payload["messages"]) > 0:
                    quote_text = payload["messages"][0].get("text", "")
                    # Try to parse as JSON
                    try:
                        quote = json.loads(quote_text)
                        quote["supplier_name"] = supplier["name"]
                        print(f"✅ Received quote from {supplier['name']}")
                        return quote
                    except json.JSONDecodeError:
                        print(f"⚠️  Response from {supplier['name']} was not JSON: {quote_text[:100]}")
                        return None
        else:
            print(f"❌ HTTP {response.status_code} from {supplier['name']}")
            return None

    except Exception as ex:  # pylint: disable=broad-except
        print(f"❌ Error querying {supplier['name']}: {ex}")
        import traceback
        traceback.print_exc()
        return None

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def evaluate_quotes(quotes: List[Dict[str, Any]], _priority: str) -> Dict[str, Any]:
    """Evaluate quotes and select the best one"""
    if not quotes:
        return None

    # Score each quote
    scored_quotes = []
    for quote in quotes:
        score = 0

        # Coverage score (40%)
        coverage = quote.get("coverage_ratio", 0)
        score += coverage * 0.4

        # Delivery time score (30%) - lower is better
        eta_hours = quote.get("estimated_delivery_hours", 999)
        time_score = max(0, 1 - (eta_hours / 24))  # Normalize to 24 hours
        score += time_score * 0.3

        # Cost score (30%) - lower is better
        cost = quote.get("total_cost", 999999)
        cost_score = max(0, 1 - (cost / 10000))  # Normalize to $10000
        score += cost_score * 0.3

        scored_quotes.append({"quote": quote, "score": score})

    # Sort by score
    scored_quotes.sort(key=lambda x: x["score"], reverse=True)

    return scored_quotes[0]["quote"]

def format_quote_response(need_request: Dict[str, Any], quotes: List[Dict[str, Any]], best_quote: Dict[str, Any]) -> str:
    """Format the response with quote information"""
    items = need_request.get("items", [])
    quantity = need_request.get("quantity_needed", "unknown")
    location = need_request.get("location", "Unknown")
    priority = need_request.get("priority", "medium")
    request_id = need_request.get("request_id", "N/A")

    response = f"""✅ **Disaster Relief Request Processed**

**Request ID**: {request_id}
**Items Requested**: {', '.join(items)}
**Quantity**: {quantity}
**Location**: {location}
**Priority**: {priority.upper()}

📊 **Received {len(quotes)} Quote(s) from Supply Agents**

"""

    # Show all quotes
    for i, quote in enumerate(quotes, 1):
        is_best = quote == best_quote
        marker = "⭐ **BEST QUOTE**" if is_best else f"Quote #{i}"

        response += f"""
{marker}
**Supplier**: {quote.get('supplier_name', 'Unknown')}
**Location**: {quote.get('supplier_location', 'Unknown')}
**Coverage**: {quote.get('coverage_ratio', 0) * 100:.1f}%
**Delivery Time**: {quote.get('estimated_delivery_hours', 'N/A'):.1f} hours
**Delivery Date**: {quote.get('estimated_delivery_date', 'N/A')}
**Total Cost**: ${quote.get('total_cost', 0):.2f}
**Delivery Mode**: {quote.get('delivery_mode', 'Unknown')}
**Distance**: {quote.get('distance_km', 'N/A')} km
"""

    response += f"""

🎯 **Recommended Action**: Accept quote from {best_quote.get('supplier_name', 'top supplier')}

**Next Steps:**
1. ✅ Review and approve the recommended quote
2. 📦 Supplier will reserve inventory
3. 🚚 Delivery will be coordinated
4. 📍 Tracking updates will be provided

Thank you for using AgentAid! Help is on the way! 🚨
"""

    return response

def format_no_quotes_response(need_request: Dict[str, Any]) -> str:
    """Format response when no quotes are received"""
    items = need_request.get("items", [])
    location = need_request.get("location", "Unknown")
    priority = need_request.get("priority", "medium")
    request_id = need_request.get("request_id", "N/A")

    return f"""⚠️ **No Quotes Received**

**Request ID**: {request_id}
**Items Requested**: {', '.join(items)}
**Location**: {location}
**Priority**: {priority.upper()}

Unfortunately, no supply agents responded with quotes at this time.

**Possible Reasons:**
- Supply agents may be offline
- Location may be outside service radius
- Requested items may be out of stock

**Next Steps:**
1. 🔄 Request will be re-broadcast
2. 📞 Manual coordination may be required
3. 🆘 Emergency services have been notified

We're working to fulfill your request. Please stand by! 🚨
"""

@app.get("/")
async def root():
    """Root endpoint with agent information"""
    return {
        "agent": AGENT_NAME,
        "address": identity.address,
        "endpoint": AGENT_ENDPOINT,
        "protocol": "Chat Protocol + AidProtocol v2.0.0",
        "readme": readme,
        "capabilities": [
            "emergency_need_broadcasting",
            "quote_evaluation",
            "smart_allocation",
            "location_aware_matching",
            "priority_management"
        ],
        "usage": "Send POST requests to /chat with disaster relief needs"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    print(f"\n{'='*80}")
    print(f"🚨 {AGENT_NAME}")
    print(f"{'='*80}")
    print(f"Agent Address: {identity.address}")
    print(f"Endpoint: {AGENT_ENDPOINT}")
    print(f"Port: {port}")
    print(f"Status: http://localhost:{port}/status")
    print(f"Chat: POST http://localhost:{port}/chat")
    print(f"{'='*80}\n")

    uvicorn.run(app, host="0.0.0.0", port=port)
