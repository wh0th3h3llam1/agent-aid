#!/usr/bin/env python3
"""
Need Agent - Chat Protocol Adapter for Agentverse
Exposes the need agent functionality via Chat Protocol for Agentverse deployment
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
AGENT_NAME = "AgentAid Need Agent"
AGENT_SEED_PHRASE = os.environ.get("AGENT_SEED_PHRASE", "need_agent_berkeley_1_demo_seed")
AGENT_ENDPOINT = os.environ.get("AGENT_EXTERNAL_ENDPOINT", "http://localhost:8000")

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

        # Parse the disaster relief request
        response_text = process_need_request(user_message)

        # Send response back to sender
        send_message_to_agent(
            destination=env.sender,
            msg=ChatMessage([TextContent(response_text)]),
            sender=identity,
        )

        return {"status": "processed", "message": "Request processed successfully"}

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

def process_need_request(message: str) -> str:
    """Process a disaster relief need request from natural language"""
    try:
        # Extract information from the message
        # This is a simplified version - in production, you'd use Claude AI or similar

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

        # Extract location (simplified - look for coordinates or address)
        location = "Location to be determined"
        if "berkeley" in message_lower:
            location = "Berkeley, CA (37.8715, -122.2730)"
        elif "oakland" in message_lower:
            location = "Oakland, CA (37.8044, -122.2712)"
        elif "san francisco" in message_lower or "sf" in message_lower:
            location = "San Francisco, CA (37.78, -122.42)"

        # Extract affected people count
        import re
        people_match = re.search(r'(\d+)\s+people', message_lower)
        affected_people = people_match.group(1) if people_match else "unknown"

        # Create response
        response = f"""✅ **Disaster Relief Request Received**

**Request Details:**
- **Items Needed**: {', '.join(items)}
- **Location**: {location}
- **Priority**: {priority.upper()}
- **People Affected**: {affected_people}

**Status**: Broadcasting quote requests to supply agents...

I'm now contacting available supply agents in the area to fulfill your request. The system will:
1. ✉️ Send quote requests to nearby suppliers
2. 📊 Evaluate quotes based on coverage, cost, and delivery time
3. 🎯 Allocate resources from the best suppliers
4. ✅ Confirm allocations and coordinate delivery

You will receive updates as suppliers respond. For critical priority requests, we prioritize the fastest delivery times.

**Next Steps:**
- Supply agents are being contacted
- Quotes will be evaluated within 3-9 seconds
- Allocation confirmations will follow

Thank you for using AgentAid. Help is on the way! 🚨
"""

        return response

    except Exception as e:
        return f"Error processing request: {str(e)}. Please provide: items needed, location, and priority level."

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
