#!/usr/bin/env python3
"""
Need Agent - Fixed Version with Agent-to-Agent Communication
Broadcasts to supply agents, collects quotes, evaluates based on quantity & ETA
"""

import os
import json
import asyncio
from typing import cast, Dict, List
from datetime import datetime
from fastapi import FastAPI
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
from uagents_core.envelope import Envelope
from uagents_core.identity import Identity
from uagents_core.utils.messages import parse_envelope, send_message_to_agent

# Agent configuration
AGENT_NAME = "AgentAid Need Agent"
AGENT_SEED_PHRASE = os.environ.get("AGENT_SEED_PHRASE", "need_agent_berkeley_1_demo_seed")
AGENT_ENDPOINT = os.environ.get("AGENT_EXTERNAL_ENDPOINT", "http://localhost:8000")

# Supply agent addresses (add all your supply agents here)
# This is the LOCAL supply agent address (running on port 8001)
SUPPLY_AGENTS = [
    "agent1q0teepydaltv70mnht98uwcxz6murcysrm782k4qge58pap4w6vaqhea6y9",  # Local supply agent
]

# Create identity from seed
identity = Identity.from_seed(AGENT_SEED_PHRASE, 0)

# Storage for active requests and quotes
active_requests = {}  # request_id -> {request_data, quotes, original_sender}
quote_timeout = 10  # seconds to wait for quotes

# Create FastAPI app
app = FastAPI(title=AGENT_NAME, description="Disaster relief need management agent")

@app.get("/status")
async def healthcheck():
    """Health check endpoint"""
    return {
        "status": "OK - Agent is running",
        "agent_name": AGENT_NAME,
        "agent_address": identity.address,
        "supply_agents": len(SUPPLY_AGENTS),
        "active_requests": len(active_requests)
    }

@app.post("/")
async def handle_message(env: Envelope):
    """Handle incoming chat messages via Chat Protocol"""
    try:
        # Parse the incoming chat message
        msg = cast(ChatMessage, parse_envelope(env, ChatMessage))
        user_message = msg.text()

        print(f"\n{'='*80}")
        print(f"📨 Received message from {env.sender}")
        print(f"Message: {user_message}")
        print(f"{'='*80}")

        # Check if this is a quote response from a supply agent
        if env.sender in SUPPLY_AGENTS or "quote" in user_message.lower():
            # This is a quote response from a supply agent
            await handle_quote_response(env.sender, user_message)
            return {"status": "quote_received"}
        else:
            # This is a new request from a user
            await process_need_request(user_message, env.sender)
            return {"status": "request_received"}

    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": str(e)}

async def process_need_request(message: str, sender: str, request: dict = None):
    """Process a disaster relief need request from user"""
    try:
        print(f"\n🔍 Processing need request...")
        
        # Extract information from the message
        message_lower = message.lower()

        # Detect priority
        priority = "medium"
        if "critical" in message_lower or "urgent" in message_lower or "emergency" in message_lower:
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

        # Extract quantity
        import re
        qty_match = re.search(r'(\d+)\s+(?:blanket|water|food|medical|supply|supplies)', message_lower)
        quantity = int(qty_match.group(1)) if qty_match else 50

        # Extract location
        location = "Location to be determined"
        if "berkeley" in message_lower:
            location = "Berkeley, CA"
        elif "oakland" in message_lower:
            location = "Oakland, CA"
        elif "san francisco" in message_lower or "sf" in message_lower:
            location = "San Francisco, CA"

        # Extract affected people count
        people_match = re.search(r'(\d+)\s+people', message_lower)
        affected_people = int(people_match.group(1)) if people_match else 0

        # Use provided request ID or create new one
        request_id = request.get("request_id", f"REQ-{int(datetime.now().timestamp() * 1000)}") if request else f"REQ-{int(datetime.now().timestamp() * 1000)}"

        # Store request
        active_requests[request_id] = {
            "request_id": request_id,
            "items": items,
            "quantity": quantity,
            "location": location,
            "priority": priority,
            "affected_people": affected_people,
            "quotes": [],
            "original_sender": sender,
            "timestamp": datetime.now().isoformat()
        }

        print(f"✅ Request created: {request_id}")
        print(f"   Items: {items}")
        print(f"   Quantity: {quantity}")
        print(f"   Location: {location}")
        print(f"   Priority: {priority}")

        # Send acknowledgment to user
        ack_message = f"""✅ **Request Received**

**Request ID**: {request_id}
**Items**: {', '.join(items)}
**Quantity**: {quantity}
**Location**: {location}
**Priority**: {priority.upper()}
**People Affected**: {affected_people}

🔄 Broadcasting to {len(SUPPLY_AGENTS)} supply agent(s)...
⏱️ Collecting quotes (this may take 10-15 seconds)..."""

        send_message_to_agent(
            destination=sender,
            msg=ChatMessage([TextContent(ack_message)]),
            sender=identity,
        )

        # Broadcast to all supply agents
        await broadcast_to_suppliers(request_id)

        # Start quote collection timer
        asyncio.create_task(collect_and_evaluate_quotes(request_id))

    except Exception as e:
        print(f"❌ Error processing request: {e}")
        error_msg = f"Error processing request: {str(e)}"
        send_message_to_agent(
            destination=sender,
            msg=ChatMessage([TextContent(error_msg)]),
            sender=identity,
        )

async def broadcast_to_suppliers(request_id: str):
    """Broadcast quote request to all supply agents"""
    try:
        request_data = active_requests[request_id]
        
        # Create quote request message
        quote_request = f"""QUOTE_REQUEST:{request_id}
Items: {', '.join(request_data['items'])}
Quantity: {request_data['quantity']}
Location: {request_data['location']}
Priority: {request_data['priority']}
People Affected: {request_data['affected_people']}

Please respond with your quote including quantity available and ETA."""

        print(f"\n📤 Broadcasting to supply agents via HTTP...")
        
        # Send HTTP request to local supply agent
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "http://localhost:8001/simple",
                    json={"message": quote_request, "sender": request_id},
                    timeout=5.0
                )
                if response.status_code == 200:
                    print(f"✅ Quote request sent to supply agent!")
                else:
                    print(f"⚠️  Supply agent returned: {response.status_code}")
            except Exception as e:
                print(f"❌ Error sending to supply agent: {e}")

    except Exception as e:
        print(f"❌ Error broadcasting: {e}")

async def handle_quote_response(supplier_address: str, message: str):
    """Handle quote response from a supply agent"""
    try:
        print(f"\n💰 Quote received from {supplier_address[:20]}...")
        print(f"Message preview: {message[:200]}...")
        
        # Extract request ID from quote
        import re
        req_id_match = re.search(r'QUOTE_RESPONSE:(\S+)', message)
        if not req_id_match:
            # Try to find request ID in message
            req_id_match = re.search(r'REQ-\d+', message)
        
        if not req_id_match:
            print("⚠️  Could not extract request ID from quote")
            print(f"Available requests: {list(active_requests.keys())}")
            return
        
        request_id = req_id_match.group(1) if 'QUOTE_RESPONSE' in message else req_id_match.group(0)
        print(f"Extracted request ID: {request_id}")
        
        if request_id not in active_requests:
            print(f"⚠️  Request {request_id} not found or already processed")
            print(f"Available requests: {list(active_requests.keys())}")
            return

        # Parse quote details (handle markdown formatting)
        qty_match = re.search(r'\*?\*?Quantity\*?\*?[:\s]+(\d+)', message, re.IGNORECASE)
        eta_match = re.search(r'\*?\*?ETA\*?\*?[:\s]+([\d.]+)\s*hours?', message, re.IGNORECASE)
        supplier_match = re.search(r'\*?\*?Supplier\*?\*?[:\s]+([^\n]+)', message, re.IGNORECASE)
        
        quote = {
            "supplier": supplier_match.group(1).strip() if supplier_match else supplier_address[:20],
            "supplier_address": supplier_address,
            "quantity": int(qty_match.group(1)) if qty_match else 0,
            "eta_hours": float(eta_match.group(1)) if eta_match else 999,
            "raw_message": message,
            "timestamp": datetime.now().isoformat()
        }

        # Add quote to request
        active_requests[request_id]["quotes"].append(quote)
        
        print(f"✅ Quote added:")
        print(f"   Supplier: {quote['supplier']}")
        print(f"   Quantity: {quote['quantity']}")
        print(f"   ETA: {quote['eta_hours']} hours")
        print(f"   Total quotes: {len(active_requests[request_id]['quotes'])}")

    except Exception as e:
        print(f"❌ Error handling quote: {e}")

async def collect_and_evaluate_quotes(request_id: str):
    """Wait for quotes and evaluate them"""
    try:
        print(f"\n⏱️  Waiting {quote_timeout} seconds for quotes...")
        await asyncio.sleep(quote_timeout)

        if request_id not in active_requests:
            print(f"⚠️  Request {request_id} no longer active")
            return

        request_data = active_requests[request_id]
        quotes = request_data["quotes"]

        print(f"\n📊 Evaluating {len(quotes)} quote(s)...")

        if not quotes:
            # No quotes received
            no_quote_msg = f"""⚠️ **No Quotes Received**

Request ID: {request_id}
Items: {', '.join(request_data['items'])}

Unfortunately, no supply agents responded with quotes. This could mean:
- Supply agents are offline
- No suppliers have the requested items
- Network connectivity issues

Please try again later or contact support."""

            send_message_to_agent(
                destination=request_data["original_sender"],
                msg=ChatMessage([TextContent(no_quote_msg)]),
                sender=identity,
            )
        else:
            # Evaluate quotes based on quantity and ETA
            best_quote = evaluate_quotes(quotes, request_data["quantity"])
            
            # Send result to user
            await send_final_result(request_id, best_quote, quotes)

        # Clean up
        del active_requests[request_id]
        print(f"✅ Request {request_id} completed and cleaned up")

    except Exception as e:
        print(f"❌ Error evaluating quotes: {e}")

def evaluate_quotes(quotes: List[Dict], requested_qty: int) -> Dict:
    """Evaluate quotes based on quantity coverage and ETA"""
    
    def score_quote(quote):
        # Score based on quantity coverage (0-100 points)
        qty_coverage = min(quote["quantity"] / requested_qty, 1.0) * 100
        
        # Score based on ETA (faster is better, 0-100 points)
        # ETA of 1 hour = 100 points, 10 hours = 0 points
        eta_score = max(0, 100 - (quote["eta_hours"] * 10))
        
        # Total score (equal weight to quantity and ETA)
        total_score = (qty_coverage * 0.5) + (eta_score * 0.5)
        
        return total_score
    
    # Score all quotes
    for quote in quotes:
        quote["score"] = score_quote(quote)
        quote["coverage_pct"] = min(quote["quantity"] / requested_qty * 100, 100)
    
    # Sort by score (highest first)
    sorted_quotes = sorted(quotes, key=lambda q: q["score"], reverse=True)
    
    print(f"\n🏆 Quote Rankings:")
    for i, quote in enumerate(sorted_quotes, 1):
        print(f"   {i}. {quote['supplier']}: Score={quote['score']:.1f}, Qty={quote['quantity']}, ETA={quote['eta_hours']}h")
    
    return sorted_quotes[0]

async def send_final_result(request_id: str, best_quote: Dict, all_quotes: List[Dict]):
    """Send final result to user"""
    try:
        # Get request data before it's deleted
        request_data = active_requests.get(request_id, {
            'items': ['unknown'],
            'quantity': 'unknown',
            'original_sender': 'unknown'
        })
        
        result_message = f"""✅ **Best Supplier Found!**

**Request ID**: {request_id}
**Items**: {', '.join(request_data['items'])}
**Quantity Requested**: {request_data['quantity']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🏆 SELECTED SUPPLIER**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Supplier**: {best_quote['supplier']}
**Quantity Available**: {best_quote['quantity']} units
**Coverage**: {best_quote['coverage_pct']:.1f}%
**Delivery Time**: {best_quote['eta_hours']} hours
**Score**: {best_quote['score']:.1f}/100

**Delivery To**: {request_data['location']}
**Priority**: {request_data['priority'].upper()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        if len(all_quotes) > 1:
            result_message += f"\n**Other Quotes Received**: {len(all_quotes) - 1}\n"
            for i, quote in enumerate(all_quotes[1:], 2):
                result_message += f"{i}. {quote['supplier']}: {quote['quantity']} units, {quote['eta_hours']}h (Score: {quote['score']:.1f})\n"

        result_message += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Next Steps**:
✅ Supplier has been notified
✅ Items are being prepared
✅ Delivery will be coordinated
✅ You will receive tracking updates

Thank you for using AgentAid! 🚨
"""

        print(f"\n📤 Sending final result to user...")
        
        # Send update to Claude service
        print(f"🔄 Calling send_update_to_claude_service for request {request_id}")
        await send_update_to_claude_service(request_id, best_quote, all_quotes)
        print(f"✅ send_update_to_claude_service completed for request {request_id}")
        
        send_message_to_agent(
            destination=request_data["original_sender"],
            msg=ChatMessage([TextContent(result_message)]),
            sender=identity,
        )
        
        print(f"✅ Final result sent!")

    except Exception as e:
        print(f"❌ Error sending final result: {e}")

async def send_update_to_claude_service(request_id: str, best_quote: Dict, all_quotes: List[Dict]):
    """Send update to Claude service so UI can display results"""
    try:
        import httpx
        
        update_data = {
            "request_id": request_id,
            "agent_id": "need_agent_berkeley_1",
            "status": "completed",
            "quotes": all_quotes,
            "best_quote": best_quote,
            "timestamp": datetime.now().isoformat()
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "http://localhost:3000/api/uagent/update",
                json=update_data
            )
            
            if response.status_code == 200:
                print(f"✅ Update sent to Claude service")
            else:
                print(f"⚠️  Failed to send update to Claude service: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error sending update to Claude service: {e}")

@app.post("/simple")
async def handle_simple_message(request: dict):
    """Handle simple HTTP messages (not uAgents protocol)"""
    try:
        message = request.get("message", "")
        sender = request.get("sender", "unknown")
        
        print(f"\n📨 Simple HTTP message from {sender}: {message}")
        
        # Process the request
        await process_need_request(message, sender, request)
        
        return {"status": "accepted", "message": "Request is being processed"}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/quote_response")
async def handle_quote_http(request: dict):
    """Handle quote response via HTTP"""
    try:
        message = request.get("message", "")
        sender = request.get("sender", "unknown")
        
        await handle_quote_response(sender, message)
        
        return {"status": "received"}
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
        "supply_agents": len(SUPPLY_AGENTS),
        "active_requests": len(active_requests),
        "capabilities": [
            "emergency_need_broadcasting",
            "quote_collection",
            "quote_evaluation",
            "smart_allocation"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    print(f"\n{'='*80}")
    print(f"🚨 {AGENT_NAME} - FIXED VERSION")
    print(f"{'='*80}")
    print(f"Agent Address: {identity.address}")
    print(f"Endpoint: {AGENT_ENDPOINT}")
    print(f"Port: {port}")
    print(f"Supply Agents: {len(SUPPLY_AGENTS)}")
    print(f"Quote Timeout: {quote_timeout}s")
    print(f"{'='*80}\n")

    uvicorn.run(app, host="0.0.0.0", port=port)
