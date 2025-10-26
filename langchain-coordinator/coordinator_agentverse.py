#!/usr/bin/env python3
"""
LangChain Coordination Agent - Agentverse Version
Sends messages directly to Fetch.ai agents deployed on Agentverse via DeltaV
"""
import os
import asyncio
from typing import Dict, Any
from anthropic import Anthropic
import httpx
import json

# Configuration - YOUR SPECIFIC ADDRESSES
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
NEED_AGENT_ADDRESS = "agent1q2h8e88wru7sl7hfy4kkrjrf4p4zqghtu7umsw2r2twkewcscnrwymnjju9"
SUPPLY_AGENT_ADDRESS = "agent1qd0kdf9py6ehfjqq6s969dcv90sj9jg594yk252926pp2z85r82z6aepahg"
CLAUDE_SERVICE_URL = os.getenv("CLAUDE_SERVICE_URL", "http://localhost:3000")

# DeltaV API endpoint for sending messages to agents
DELTAV_API_URL = "https://agentverse.ai/v1/chat/send"
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY", "")  # You'll need this

# Verify API key is set
if not ANTHROPIC_API_KEY:
    print("❌ ERROR: ANTHROPIC_API_KEY not set in environment!")
    print("   Please run: export ANTHROPIC_API_KEY='your-key-here'")
    exit(1)

# Initialize Claude
client = Anthropic(api_key=ANTHROPIC_API_KEY)

class CoordinatorAgent:
    def __init__(self):
        self.processed_requests = set()
        
    async def analyze_request(self, user_input: str) -> Dict[str, Any]:
        """Use Claude to analyze the disaster request and extract details"""
        
        prompt = f"""Analyze this disaster relief request and extract structured information.

User Request: "{user_input}"

Extract and return JSON with:
1. items: list of items needed (e.g., ["blankets", "water bottles"])
2. quantity: estimated quantity for main item
3. priority: "critical", "high", "medium", or "low" based on urgency indicators
4. location: any location mentioned (city, address, coordinates)
5. contact: phone/email if mentioned
6. victim_count: estimated number of people affected
7. urgency_indicators: keywords that indicate priority

Priority Guidelines:
- CRITICAL: Life-threatening, immediate danger, medical emergency, "urgent", "emergency"
- HIGH: Significant need, large group affected, time-sensitive, "ASAP", "quickly"
- MEDIUM: Important but not immediate, moderate group size
- LOW: General request, small scale, flexible timing

Return ONLY valid JSON, no explanation."""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = response.content[0].text
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(content)
            
            print(f"\n🤖 Claude Analysis:")
            print(f"   Items: {analysis.get('items', [])}")
            print(f"   Priority: {analysis.get('priority', 'medium').upper()}")
            print(f"   Quantity: {analysis.get('quantity', 'unknown')}")
            print(f"   Location: {analysis.get('location', 'Not specified')}")
            print(f"   Victim Count: {analysis.get('victim_count', 0)}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing request: {e}")
            return {
                "items": ["blankets"],
                "quantity": 50,
                "priority": "high",
                "location": "",
                "contact": "",
                "victim_count": 0,
                "urgency_indicators": []
            }
    
    def format_message_for_need_agent(self, analysis: Dict[str, Any]) -> str:
        """Format the analyzed request into a natural language message for the need agent"""
        
        items_str = ", ".join(analysis.get('items', ['supplies']))
        quantity = analysis.get('quantity', 'unknown')
        location = analysis.get('location', 'location to be determined')
        priority = analysis.get('priority', 'medium')
        victim_count = analysis.get('victim_count', 0)
        contact = analysis.get('contact', '')
        
        # Create a natural language message that the need agent can parse
        message = f"We need {quantity} {items_str} at {location}. "
        message += f"This is {priority} priority. "
        
        if victim_count:
            message += f"{victim_count} people affected. "
        
        if contact:
            message += f"Contact: {contact}. "
        
        message += "Please coordinate with supply agents to fulfill this request."
        
        return message
    
    async def send_to_agentverse_via_deltav(self, message: str) -> bool:
        """
        Send message to Need Agent on Agentverse via DeltaV Chat API
        
        NOTE: This requires an Agentverse API key and uses the DeltaV chat endpoint
        For now, we'll simulate this and provide instructions
        """
        
        print(f"\n📤 Sending to Need Agent on Agentverse...")
        print(f"   Need Agent: {NEED_AGENT_ADDRESS}")
        print(f"   Message: {message[:100]}...")
        
        # METHOD 1: Via DeltaV Chat (requires Agentverse API key)
        if AGENTVERSE_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=30) as http_client:
                    response = await http_client.post(
                        "https://agentverse.ai/v1beta1/engine/chat/sessions",
                        headers={
                            "Authorization": f"Bearer {AGENTVERSE_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "agent_address": NEED_AGENT_ADDRESS,
                            "message": message
                        }
                    )
                    
                    if response.status_code in [200, 201]:
                        print(f"✅ Message sent to Agentverse!")
                        return True
                    else:
                        print(f"⚠️  Agentverse returned: {response.status_code}")
                        print(f"   Response: {response.text[:200]}")
                        return False
                        
            except Exception as e:
                print(f"❌ Error sending to Agentverse: {e}")
                return False
        
        # METHOD 2: Manual instructions (if no API key)
        else:
            print(f"\n💡 TO SEND THIS MESSAGE TO YOUR AGENT:")
            print(f"=" * 70)
            print(f"1. Go to: https://agentverse.ai")
            print(f"2. Find your agent: {NEED_AGENT_ADDRESS[:20]}...")
            print(f"3. Use the Chat interface")
            print(f"4. Send this message:")
            print(f"   \"{message}\"")
            print(f"=" * 70)
            print(f"\nOR set AGENTVERSE_API_KEY to automate this")
            return False
    
    async def process_chat_message(self, user_message: str, request_id: str = None) -> Dict[str, Any]:
        """Process a chat message from the user"""
        
        print(f"\n{'='*70}")
        print(f"📨 New Message: {user_message[:100]}...")
        print(f"{'='*70}")
        
        # Step 1: Analyze with Claude
        analysis = await self.analyze_request(user_message)
        
        # Step 2: Store in Claude service
        try:
            async with httpx.AsyncClient(timeout=30) as http_client:
                response = await http_client.post(
                    f"{CLAUDE_SERVICE_URL}/api/extract",
                    json={
                        "input": user_message,
                        "source": "chat",
                        "analysis": analysis
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    stored_request_id = data.get("data", {}).get("request_id") or \
                                data.get("partial_data", {}).get("request_id") or \
                                request_id or \
                                f"REQ-{int(asyncio.get_event_loop().time())}"
                    
                    print(f"\n✅ Request stored: {stored_request_id}")
                    
                    # Step 3: Format message for need agent
                    need_agent_message = self.format_message_for_need_agent(analysis)
                    
                    # Step 4: Send to Agentverse
                    await self.send_to_agentverse_via_deltav(need_agent_message)
                    
                    return {
                        "success": True,
                        "request_id": stored_request_id,
                        "analysis": analysis,
                        "message": f"✅ Request analyzed! Priority: {analysis.get('priority', 'medium').upper()}. "
                                  f"To complete: Send message to your agent on Agentverse."
                    }
                    
        except Exception as e:
            print(f"❌ Error processing: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process request."
            }
    
    async def poll_and_coordinate(self):
        """Poll for new chat messages and coordinate"""
        print(f"\n🔄 Coordinator polling for chat messages...")
        print(f"   Service: {CLAUDE_SERVICE_URL}")
        print(f"   Need Agent: {NEED_AGENT_ADDRESS[:20]}...")
        print(f"   Supply Agent: {SUPPLY_AGENT_ADDRESS[:20]}...")
        print(f"   Polling interval: 5 seconds\n")
        
        while True:
            try:
                async with httpx.AsyncClient(timeout=10) as http_client:
                    response = await http_client.get(f"{CLAUDE_SERVICE_URL}/api/uagent/pending-requests")
                    
                    if response.status_code == 200:
                        data = response.json()
                        requests = data.get("requests", [])
                        
                        for req in requests:
                            req_id = req.get("request_id")
                            if req_id not in self.processed_requests:
                                original_input = req.get("raw_input") or req.get("input", "")
                                
                                if original_input:
                                    await self.process_chat_message(original_input, request_id=req_id)
                                    self.processed_requests.add(req_id)
                                else:
                                    self.processed_requests.add(req_id)
                
            except Exception as e:
                print(f"❌ Polling error: {e}")
            
            await asyncio.sleep(5)

async def main():
    """Main entry point"""
    print("=" * 70)
    print("🧠 LangChain Coordination Agent - AGENTVERSE")
    print("=" * 70)
    print(f"   Claude Model: claude-sonnet-4-20250514")
    print(f"   Service: {CLAUDE_SERVICE_URL}")
    print(f"   Need Agent: {NEED_AGENT_ADDRESS}")
    print(f"   Supply Agent: {SUPPLY_AGENT_ADDRESS}")
    print("=" * 70)
    
    if not ANTHROPIC_API_KEY:
        print("\n❌ ERROR: ANTHROPIC_API_KEY not found!")
        return
    
    print(f"\n✅ Anthropic API Key: {ANTHROPIC_API_KEY[:20]}...")
    
    if AGENTVERSE_API_KEY:
        print(f"✅ Agentverse API Key: {AGENTVERSE_API_KEY[:20]}...")
    else:
        print(f"⚠️  No Agentverse API Key - will show manual instructions")
    
    coordinator = CoordinatorAgent()
    
    # Test mode
    if os.getenv("TEST_MODE") == "true":
        print("\n🧪 TEST MODE\n")
        result = await coordinator.process_chat_message(
            "Emergency! We need 100 blankets urgently in San Francisco. "
            "About 200 people affected. Contact: 555-1234"
        )
        print(f"\n📊 Result: {json.dumps(result, indent=2)}")
    else:
        print("\n🚀 Starting polling mode...\n")
        await coordinator.poll_and_coordinate()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Coordinator shutting down...")
