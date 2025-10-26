#!/usr/bin/env python3
"""
Auto-processor that polls Claude service and triggers agents to process pending requests
"""

import asyncio
import httpx
import time
from datetime import datetime

async def process_pending_requests():
    """Poll Claude service and trigger need agent to process pending requests"""
    
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Get pending requests
                response = await client.get("http://localhost:3000/api/uagent/pending-requests")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") and data.get("requests"):
                        requests = data["requests"]
                        print(f"📋 Found {len(requests)} pending requests")
                        
                        # Process the first pending request
                        if requests:
                            req = requests[0]
                            print(f"🚀 Processing request: {req['request_id']}")
                            print(f"   Items: {req['items']}")
                            print(f"   Quantity: {req['quantity']}")
                            print(f"   Priority: {req['priority']}")
                            
                            # Create a simple message for the need agent
                            message = f"We need {req['quantity']} {', '.join(req['items'])}"
                            if req.get('location', {}).get('address'):
                                message += f" at {req['location']['address']}"
                            
                            # Send to need agent with original request ID
                            agent_response = await client.post(
                                "http://localhost:8000/simple",
                                json={
                                    "message": message,
                                    "user": "auto_processor",
                                    "request_id": req['request_id']
                                }
                            )
                            
                            if agent_response.status_code == 200:
                                print(f"✅ Request sent to need agent")
                            else:
                                print(f"❌ Failed to send to need agent: {agent_response.status_code}")
                    else:
                        print("📭 No pending requests")
                else:
                    print(f"❌ Failed to get pending requests: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Wait 30 seconds before checking again
        await asyncio.sleep(30)

async def main():
    """Main function"""
    print("🤖 AgentAid Auto-Processor")
    print("=" * 40)
    print("Polling Claude service for pending requests...")
    print("Will process requests every 30 seconds")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    try:
        await process_pending_requests()
    except KeyboardInterrupt:
        print("\n🛑 Auto-processor stopped")

if __name__ == "__main__":
    asyncio.run(main())
