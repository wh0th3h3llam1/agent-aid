#!/usr/bin/env python3
"""
Test the complete agent communication flow
"""
import asyncio
import httpx
import time

async def test_full_flow():
    """Test complete disaster request flow"""
    
    print("🧪 Testing Complete Agent Communication Flow\n")
    print("=" * 60)
    
    # Step 1: Check services are running
    print("\n📋 Step 1: Checking Services")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            health = await client.get("http://localhost:3000/health")
            if health.status_code == 200:
                print("   ✅ Claude service is running")
            else:
                print("   ❌ Claude service not responding")
                return
    except Exception as e:
        print(f"   ❌ Claude service error: {e}")
        return
    
    # Step 2: Submit a test request
    print("\n📋 Step 2: Submitting Test Request")
    request_data = {
        "input": "We need 50 blankets at 456 Oak Street, Berkeley. Contact: 555-9999. About 100 people affected. This is urgent!",
        "source": "test_flow"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "http://localhost:3000/api/extract",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    request_id = data.get("data", {}).get("request_id")
                    items = data.get("data", {}).get("items", [])
                    print(f"   ✅ Request submitted: {request_id}")
                    print(f"   Items: {items}")
                    print(f"   Complete: {not data.get('needs_followup', True)}")
                else:
                    print(f"   ❌ Request failed: {data}")
                    return
            else:
                print(f"   ❌ HTTP {response.status_code}")
                return
    except Exception as e:
        print(f"   ❌ Error submitting request: {e}")
        return
    
    # Step 3: Wait for coordination agent to poll (polls every 10 seconds)
    print("\n📋 Step 3: Waiting for Coordination Agent (15 seconds)")
    print("   The coordination agent polls every 10 seconds...")
    for i in range(15, 0, -1):
        print(f"   ⏳ {i} seconds remaining...", end="\r")
        await asyncio.sleep(1)
    print("   ✅ Wait complete" + " " * 30)
    
    # Step 4: Check if request is still pending
    print("\n📋 Step 4: Checking Request Status")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            pending = await client.get("http://localhost:3000/api/uagent/pending-requests")
            
            if pending.status_code == 200:
                data = pending.json()
                count = data.get("count", 0)
                
                if count == 0:
                    print("   ✅ No pending requests - agents processed it!")
                else:
                    print(f"   ⚠️  Still {count} pending request(s)")
                    print("   This means agents are NOT communicating properly")
                    
                    # Show the pending requests
                    for req in data.get("requests", [])[:1]:
                        print(f"\n   Request Details:")
                        print(f"      ID: {req.get('request_id')}")
                        print(f"      Items: {req.get('items')}")
                        print(f"      Status: {req.get('status')}")
    except Exception as e:
        print(f"   ❌ Error checking status: {e}")
    
    # Step 5: Check for any updates
    print("\n📋 Step 5: Checking for Agent Updates")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            updates = await client.get("http://localhost:3000/api/uagent/updates")
            
            if updates.status_code == 200:
                data = updates.json()
                updates_list = data.get("updates", [])
                
                if updates_list:
                    print(f"   ✅ Found {len(updates_list)} update(s)")
                    for update in updates_list[:3]:
                        print(f"      - {update.get('type')}: {update.get('message', 'N/A')[:50]}")
                else:
                    print("   ⚠️  No updates from agents")
    except Exception as e:
        print(f"   ❌ Error checking updates: {e}")
    
    # Step 6: Check all requests
    print("\n📋 Step 6: Checking All Requests in System")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            all_req = await client.get("http://localhost:3000/api/requests")
            
            if all_req.status_code == 200:
                data = all_req.json()
                total = data.get("total", 0)
                print(f"   Total requests: {total}")
                
                if total > 0:
                    print(f"   By priority: {data.get('by_priority', {})}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 7: Diagnosis
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS")
    print("=" * 60)
    
    # Re-check pending
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            pending = await client.get("http://localhost:3000/api/uagent/pending-requests")
            data = pending.json()
            count = data.get("count", 0)
            
            if count == 0:
                print("\n✅ SUCCESS: Agents are communicating and processing requests!")
                print("   The UI should work correctly now.")
            else:
                print("\n❌ PROBLEM: Agents are NOT processing requests")
                print("\nPossible issues:")
                print("   1. Coordination agent not polling")
                print("   2. Coordination agent not finding agents in registry")
                print("   3. Supply/Need agents not receiving messages")
                print("   4. Protocol handlers not registered correctly")
                print("\nTo debug:")
                print("   - Check agent logs for 'Received QuoteRequest' messages")
                print("   - Verify agent addresses match in environment variables")
                print("   - Ensure all agents have AidProtocol included")
    except Exception as e:
        print(f"❌ Error in diagnosis: {e}")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
