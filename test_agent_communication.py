#!/usr/bin/env python3
"""
Test agent communication by checking if coordination agent can see other agents
"""
import os
import sys
import time
import asyncio
import httpx

async def test_coordination():
    """Test if coordination agent is processing requests"""
    
    print("🔍 Testing Agent Communication\n")
    
    # Wait for agents to fully start
    print("⏳ Waiting for agents to initialize...")
    await asyncio.sleep(5)
    
    # Check pending requests
    print("\n📋 Checking pending requests...")
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get("http://localhost:3000/api/uagent/pending-requests")
        data = response.json()
        
        if data.get("success"):
            count = data.get("count", 0)
            print(f"   Found {count} pending request(s)")
            
            if count > 0:
                print("\n   Requests:")
                for req in data.get("requests", []):
                    print(f"   - {req['request_id']}: {req['items']} (status: {req['status']})")
        else:
            print("   ❌ Failed to get pending requests")
    
    # Wait for coordination agent to process (polls every 10 seconds)
    print("\n⏳ Waiting 20 seconds for coordination agent to process...")
    await asyncio.sleep(20)
    
    # Check again
    print("\n📋 Checking pending requests again...")
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get("http://localhost:3000/api/uagent/pending-requests")
        data = response.json()
        
        if data.get("success"):
            count = data.get("count", 0)
            print(f"   Found {count} pending request(s)")
            
            if count > 0:
                print("   ⚠️  Requests are still pending - agents may not be communicating")
            else:
                print("   ✅ Requests processed!")
        
        # Check for updates
        print("\n📊 Checking for agent updates...")
        updates_response = await client.get("http://localhost:3000/api/uagent/updates")
        updates_data = updates_response.json()
        
        if updates_data.get("success"):
            updates = updates_data.get("updates", [])
            print(f"   Found {len(updates)} update(s)")
            for update in updates[:5]:  # Show first 5
                print(f"   - {update.get('type', 'unknown')}: {update.get('message', 'N/A')}")
        
        # Check all requests
        print("\n📋 Checking all requests...")
        all_response = await client.get("http://localhost:3000/api/requests")
        all_data = all_response.json()
        
        if all_data.get("success"):
            total = all_data.get("total", 0)
            print(f"   Total requests in system: {total}")

if __name__ == "__main__":
    asyncio.run(test_coordination())
