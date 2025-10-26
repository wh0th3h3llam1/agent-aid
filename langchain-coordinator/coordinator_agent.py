#!/usr/bin/env python3
"""
LangChain Coordination Agent
Uses Claude to analyze requests and coordinate with Fetch.ai agents
"""
import os
import asyncio
from typing import Dict, Any, List
from anthropic import Anthropic
import httpx
import json

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
NEED_AGENT_ADDRESS = os.getenv("NEED_AGENT_ADDRESS", "")
CLAUDE_SERVICE_URL = os.getenv("CLAUDE_SERVICE_URL", "http://localhost:3000")

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
4. location: any location mentioned
5. contact: phone/email if mentioned
6. victim_count: estimated number of people affected
7. urgency_indicators: keywords that indicate priority (e.g., "urgent", "emergency", "life-threatening")

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
            print(f"   Urgency Indicators: {analysis.get('urgency_indicators', [])}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing request: {e}")
            # Fallback to basic extraction
            return {
                "items": ["blankets"],
                "quantity": 50,
                "priority": "high",
                "location": "",
                "contact": "",
                "victim_count": 0,
                "urgency_indicators": []
            }
    
    async def send_to_need_agent(self, request_data: Dict[str, Any]) -> bool:
        """Send request to Fetch.ai need agent"""
        
        if not NEED_AGENT_ADDRESS:
            print("⚠️  Need agent address not configured")
            return False
        
        try:
            # In production, this would use uagents to send message
            # For now, we'll use the Claude service as intermediary
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{CLAUDE_SERVICE_URL}/api/uagent/forward-to-need-agent",
                    json={
                        "need_agent_address": NEED_AGENT_ADDRESS,
                        "request_data": request_data
                    }
                )
                
                if response.status_code == 200:
                    print(f"✅ Forwarded to need agent")
                    return True
                else:
                    print(f"❌ Failed to forward: HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error sending to need agent: {e}")
            return False
    
    async def process_chat_message(self, user_message: str) -> Dict[str, Any]:
        """Process a chat message from the user"""
        
        print(f"\n{'='*60}")
        print(f"📨 New Message: {user_message}")
        print(f"{'='*60}")
        
        # Step 1: Analyze with Claude
        analysis = await self.analyze_request(user_message)
        
        # Step 2: Create structured request
        request_data = {
            "input": user_message,
            "source": "chat",
            "analysis": analysis
        }
        
        # Step 3: Send to Claude service for storage
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{CLAUDE_SERVICE_URL}/api/extract",
                    json=request_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    request_id = data.get("data", {}).get("request_id") or \
                                data.get("partial_data", {}).get("request_id")
                    
                    print(f"\n✅ Request stored: {request_id}")
                    
                    # Step 4: Forward to need agent if configured
                    if NEED_AGENT_ADDRESS:
                        await self.send_to_need_agent({
                            "request_id": request_id,
                            **analysis
                        })
                    
                    return {
                        "success": True,
                        "request_id": request_id,
                        "analysis": analysis,
                        "message": f"Request received! Priority: {analysis.get('priority', 'medium').upper()}. "
                                  f"Coordinating with {len(analysis.get('items', []))} supplier(s)..."
                    }
                    
        except Exception as e:
            print(f"❌ Error processing: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process request. Please try again."
            }
    
    async def poll_and_coordinate(self):
        """Poll for new chat messages and coordinate"""
        print(f"\n🔄 Coordinator polling for chat messages...")
        print(f"   Service: {CLAUDE_SERVICE_URL}")
        print(f"   Need Agent: {NEED_AGENT_ADDRESS or 'Not configured'}\n")
        
        while True:
            try:
                # Check for new messages from chat
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(f"{CLAUDE_SERVICE_URL}/api/chat/pending")
                    
                    if response.status_code == 200:
                        data = response.json()
                        messages = data.get("messages", [])
                        
                        for msg in messages:
                            msg_id = msg.get("id")
                            if msg_id not in self.processed_requests:
                                result = await self.process_chat_message(msg.get("text", ""))
                                self.processed_requests.add(msg_id)
                                
                                # Send response back
                                await client.post(
                                    f"{CLAUDE_SERVICE_URL}/api/chat/respond",
                                    json={
                                        "message_id": msg_id,
                                        "response": result.get("message", "Processing...")
                                    }
                                )
                
            except Exception as e:
                print(f"❌ Polling error: {e}")
            
            await asyncio.sleep(3)

async def main():
    """Main entry point"""
    print("=" * 60)
    print("🧠 LangChain Coordination Agent")
    print("=" * 60)
    print(f"   Claude Model: claude-sonnet-4-20250514")
    print(f"   Service: {CLAUDE_SERVICE_URL}")
    print(f"   Need Agent: {NEED_AGENT_ADDRESS or 'Not configured'}")
    print("=" * 60)
    
    coordinator = CoordinatorAgent()
    
    # Test with a sample message
    if os.getenv("TEST_MODE") == "true":
        result = await coordinator.process_chat_message(
            "Emergency! We need 100 blankets urgently in San Francisco. "
            "About 200 people affected. Contact: 555-1234"
        )
        print(f"\n📊 Result: {result}")
    else:
        # Start polling mode
        await coordinator.poll_and_coordinate()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Coordinator shutting down...")
