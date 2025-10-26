#!/usr/bin/env python3
"""
Test coordination agent directly to see if it's processing
"""
import os
import sys
import asyncio
import httpx
from pathlib import Path

# Set environment variables
os.environ['NEED_AGENT_ADDRS'] = 'agent1qgw06us8yrrmnx40dq7vlm5vqyd25tv3qx3kyax9x5k2kz7kuguxjy4a8hu'
os.environ['SUPPLY_AGENT_ADDRS'] = 'agent1qvp9jjj2rjtnj5nhnrnvmnm856l8t6gs7uyjw9ucpunepz9fmvpr5r4q8q3,agent1qf4u39wdxxdpucmt2t49dr0jw80f9cqlyqwvhue8yrayg9hf7r08j8cd9mn'

sys.path.insert(0, str(Path(__file__).parent / "agentaid-marketplace"))

async def test_coordination_logic():
    """Test the coordination agent logic"""
    
    print("🔍 Testing Coordination Agent Logic\n")
    
    # Simulate what the coordination agent does
    NEED_AGENT_ADDRESSES = [a.strip() for a in os.getenv("NEED_AGENT_ADDRS", "").split(",") if a.strip()]
    SUPPLY_AGENT_ADDRESSES = [a.strip() for a in os.getenv("SUPPLY_AGENT_ADDRS", "").split(",") if a.strip()]
    
    print(f"📋 Agent Registry:")
    print(f"   Need Agents: {len(NEED_AGENT_ADDRESSES)}")
    for addr in NEED_AGENT_ADDRESSES:
        print(f"      - {addr[:30]}...")
    print(f"   Supply Agents: {len(SUPPLY_AGENT_ADDRESSES)}")
    for addr in SUPPLY_AGENT_ADDRESSES:
        print(f"      - {addr[:30]}...")
    
    # Check if we can fetch pending requests
    print(f"\n🔍 Fetching pending requests from Claude service...")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("http://localhost:3000/api/uagent/pending-requests")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Successfully fetched requests")
                print(f"   Count: {data.get('count', 0)}")
                
                if data.get("success") and data.get("requests"):
                    print(f"\n📦 Pending Requests:")
                    for req_data in data["requests"]:
                        request_id = req_data.get("request_id")
                        items = req_data.get("items", [])
                        priority = req_data.get("priority", "unknown")
                        
                        print(f"\n   Request: {request_id}")
                        print(f"      Items: {items}")
                        print(f"      Priority: {priority}")
                        
                        # Check if we would process this
                        if NEED_AGENT_ADDRESSES and SUPPLY_AGENT_ADDRESSES:
                            print(f"      ✅ Would be assigned to agents")
                        else:
                            print(f"      ❌ Would be SKIPPED (no agents available)")
                else:
                    print(f"   No pending requests found")
            else:
                print(f"   ❌ Failed to fetch requests: HTTP {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n💡 Conclusion:")
    if NEED_AGENT_ADDRESSES and SUPPLY_AGENT_ADDRESSES:
        print(f"   ✅ Agent addresses are configured")
        print(f"   ✅ Can fetch pending requests")
        print(f"   ⚠️  If requests aren't processing, the coordination agent may not be polling")
    else:
        print(f"   ❌ Agent addresses are NOT configured")

if __name__ == "__main__":
    asyncio.run(test_coordination_logic())
