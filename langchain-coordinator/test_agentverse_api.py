#!/usr/bin/env python3
"""
Test Agentverse API connection
"""
import asyncio
import httpx
import os

AGENTVERSE_API_KEY = "eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjE3NjE0NTk5NzEsImlhdCI6MTc2MTQ1NjM3MSwiaXNzIjoiZmV0Y2guYWkiLCJqdGkiOiI5NGE4MDYwOTQ5NzNhOWNkMDBkMWU1MDEiLCJzY29wZSI6IiIsInN1YiI6IjlhYzEwODJiZDk1Nzg3MjNiMTNkZDBkOTE1MDBmODQxNjk0ZjQ4NzQ4YzRhYjU1NCJ9.aVVYcTIAKOB7OLRRDEBc2iR7jdo9WFpI1u3Fh_AJuNmVCCj0liaTzQjWg4TwznXxJJsp4ingCZ6nyySbxaKZUW5NycZdbuRUcyCpGntyAdVzC5kwLupVAnIuQ8sC7j0B29wYEBYfGEiwOkY1Sfjh9oKZenK5dF75303d-y-mgmGpcygQmkEY7WR_LVS57VRL-MkPEh7rXKh9ZMtsC-CuRRlzL5SAZDD39Pmr50WKUiBfVJMbOun330y0BjpaUQjdGIHHFIN9yQfE8HMJIqmKK4PbwUn9MBj0GA0R_gl5WQTJIsiAiyaZjtulbUZhhDbpDxbQ5sJqfpmcKNg-O2Wtkg"
NEED_AGENT_ADDRESS = "agent1q2h8e88wru7sl7hfy4kkrjrf4p4zqghtu7umsw2r2twkewcscnrwymnjju9"

async def test_agentverse_api():
    """Test sending a message to Agentverse"""
    
    message = "We need 50 blankets at Oakland. This is critical priority. 100 people affected."
    
    print("🧪 Testing Agentverse API")
    print("=" * 70)
    print(f"Agent Address: {NEED_AGENT_ADDRESS}")
    print(f"Message: {message}")
    print("=" * 70)
    
    # Try different endpoints
    endpoints = [
        ("POST", "https://agentverse.ai/v1beta1/engine/chat/sessions", {
            "agent_address": NEED_AGENT_ADDRESS,
            "message": message
        }),
        ("POST", "https://agentverse.ai/v1/chat/send", {
            "agent_address": NEED_AGENT_ADDRESS,
            "message": message
        }),
        ("POST", f"https://agentverse.ai/v1/agents/{NEED_AGENT_ADDRESS}/messages", {
            "content": message
        })
    ]
    
    async with httpx.AsyncClient(timeout=30) as client:
        for method, url, payload in endpoints:
            print(f"\n📤 Trying: {method} {url}")
            try:
                response = await client.request(
                    method,
                    url,
                    headers={
                        "Authorization": f"Bearer {AGENTVERSE_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
                if response.status_code in [200, 201, 202]:
                    print(f"   ✅ SUCCESS!")
                    return True
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("❌ None of the endpoints worked")
    print("\n💡 Alternative: Use DeltaV Chat UI")
    print("   1. Go to: https://deltav.agentverse.ai")
    print("   2. Search for your agent address")
    print("   3. Send message via chat interface")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_agentverse_api())
