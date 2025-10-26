#!/usr/bin/env python3
"""
Test to verify the AgentAid system is working correctly
"""
import asyncio
import httpx
import json

async def test_system():
    """Test the complete system"""
    
    print("🧪 AgentAid System Test")
    print("=" * 60)
    
    # Step 1: Submit a request with good location
    print("\n📋 Step 1: Submitting Request")
    print("   Location: San Francisco (should be within supplier radius)")
    
    request_data = {
        "input": "We need 50 blankets at San Francisco City Hall, 1 Dr Carlton B Goodlett Pl, San Francisco, CA 94102. Contact: 555-TEST. Urgent!",
        "source": "system_test"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "http://localhost:3000/api/extract",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("data", {}).get("request_id") or data.get("partial_data", {}).get("request_id")
                print(f"   ✅ Request submitted: {request_id}")
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 2: Wait for agents to poll and process
    print("\n📋 Step 2: Waiting for Agents (10 seconds)")
    print("   Supply agents poll every 5 seconds...")
    
    for i in range(10, 0, -1):
        print(f"   ⏳ {i} seconds...", end="\r")
        await asyncio.sleep(1)
    print("   ✅ Wait complete" + " " * 20)
    
    # Step 3: Check for updates
    print("\n📋 Step 3: Checking Agent Updates")
    
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://localhost:3000/api/uagent/updates")
            
            if response.status_code == 200:
                data = response.json()
                updates = data.get("updates", [])
                
                if updates:
                    print(f"   ✅ Found {len(updates)} update(s)!")
                    print("\n   📦 Quotes Received:")
                    
                    for update in updates[-4:]:  # Show last 4
                        agent_id = update.get("agent_id")
                        update_data = update.get("data", {})
                        supplier_label = update_data.get("supplier_label", agent_id)
                        items = update_data.get("items", [])
                        total_cost = update_data.get("total_cost", 0)
                        eta = update_data.get("eta_hours", 0)
                        
                        if items:
                            item = items[0]
                            print(f"\n      🏢 {supplier_label}")
                            print(f"         Item: {item.get('qty')} {item.get('name')} @ ${item.get('unit_price')}")
                            print(f"         Total: ${total_cost}")
                            print(f"         ETA: {eta:.1f} hours")
                    
                    return True
                else:
                    print("   ⚠️  No updates yet")
                    return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return False

async def main():
    """Main test"""
    success = await test_system()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ SUCCESS: System is working!")
        print("\nThe agents are:")
        print("   ✅ Polling for requests")
        print("   ✅ Processing requests")
        print("   ✅ Sending quotes")
        print("\n💡 The UI should now show quotes instead of being stuck!")
        print("   Open: http://localhost:3000/disaster-response.html")
    else:
        print("❌ FAILED: System not working properly")
        print("\nTroubleshooting:")
        print("   1. Check if services are running: ps aux | grep supply_agent_polling")
        print("   2. Check Claude service: curl http://localhost:3000/health")
        print("   3. Check pending requests: curl http://localhost:3000/api/uagent/pending-requests")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
