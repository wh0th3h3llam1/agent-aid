#!/usr/bin/env python3
"""
Registration script for Need Agent on Agentverse
Run this after starting the need_agent_chat_adapter.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from uagents_core.identity import Identity
except ImportError:
    print("❌ uagents_core not installed. Install with: pip install uagents-core")
    sys.exit(1)

# Configuration
AGENT_SEED_PHRASE = os.environ.get("AGENT_SEED_PHRASE", "need_agent_berkeley_1_demo_seed")
AGENT_ENDPOINT = os.environ.get("AGENT_EXTERNAL_ENDPOINT")
AGENTVERSE_API_KEY = os.environ.get("AGENTVERSE_API_KEY")

if not AGENT_ENDPOINT:
    print("❌ AGENT_EXTERNAL_ENDPOINT environment variable is required")
    print("Example: export AGENT_EXTERNAL_ENDPOINT='https://abc123.trycloudflare.com'")
    sys.exit(1)

if not AGENTVERSE_API_KEY:
    print("⚠️  AGENTVERSE_API_KEY not set. You'll need to provide it in the Agentverse UI")

# Create identity
identity = Identity.from_seed(AGENT_SEED_PHRASE, 0)

# Agent metadata
name = "AgentAid Need Agent"
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

## Integration
Part of the AgentAid Disaster Response Platform
"""

print("=" * 80)
print("🚨 AgentAid Need Agent Registration")
print("=" * 80)
print(f"\nAgent Configuration:")
print(f"  Name: {name}")
print(f"  Address: {identity.address}")
print(f"  Endpoint: {AGENT_ENDPOINT}")
print(f"  Seed: {AGENT_SEED_PHRASE[:20]}...")
print("\n" + "=" * 80)

print("\n📋 Registration Steps:")
print("\n1. Go to https://agentverse.ai/")
print("2. Navigate to 'Agents' tab")
print("3. Click 'Launch an Agent'")
print("4. Select 'Chat Protocol'")
print("5. Enter:")
print(f"   - Agent Name: {name}")
print(f"   - Agent Public Endpoint URL: {AGENT_ENDPOINT}")
print("\n6. Copy and run the registration script provided by Agentverse")
print("   (Or use the information above)")
print("\n7. Click 'Evaluate Registration'")

print("\n" + "=" * 80)
print("📝 Agent Information for Agentverse:")
print("=" * 80)
print(f"Agent Address: {identity.address}")
print(f"Endpoint: {AGENT_ENDPOINT}")
print(f"Protocol: Chat Protocol + AidProtocol v2.0.0")
print("\n" + "=" * 80)

print("\n✅ Agent is ready for registration!")
print("\nMake sure your agent is running:")
print(f"  python agents/need_agent_chat_adapter.py")
print(f"\nTest the endpoint:")
print(f"  curl {AGENT_ENDPOINT}/status")
print("\n" + "=" * 80)
