#!/usr/bin/env python3
"""
Registration script for Supply Agent on Agentverse
Run this after starting the supply_agent_chat_adapter.py
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
AGENT_SEED_PHRASE = os.environ.get("AGENT_SEED_PHRASE", "supply_sf_store_1_demo_seed")
AGENT_ENDPOINT = os.environ.get("AGENT_EXTERNAL_ENDPOINT")
AGENTVERSE_API_KEY = os.environ.get("AGENTVERSE_API_KEY")
SUPPLIER_LOCATION = os.environ.get("SUPPLIER_LABEL", "SF Depot")

if not AGENT_ENDPOINT:
    print("❌ AGENT_EXTERNAL_ENDPOINT environment variable is required")
    print("Example: export AGENT_EXTERNAL_ENDPOINT='https://def456.trycloudflare.com'")
    sys.exit(1)

if not AGENTVERSE_API_KEY:
    print("⚠️  AGENTVERSE_API_KEY not set. You'll need to provide it in the Agentverse UI")

# Create identity
identity = Identity.from_seed(AGENT_SEED_PHRASE, 0)

# Agent metadata
name = "AgentAid Supply Agent"
readme = f"""# AgentAid Supply Agent

## Overview
This agent represents disaster relief suppliers with inventory management capabilities. It responds to quote requests from need agents and manages resource allocation based on availability, location, and delivery capacity.

## Capabilities
- 📦 **Inventory Management**: Tracks available disaster relief supplies in real-time
- 💰 **Smart Quoting**: Generates quotes based on distance, priority, and availability
- 🚚 **Delivery Coordination**: Calculates ETAs and manages delivery logistics
- 🌍 **Radius-Based Service**: Only services requests within operational radius
- ⚡ **Priority Pricing**: Adjusts pricing based on emergency priority levels

## Service Area
- **Location**: {SUPPLIER_LOCATION}
- **Service Radius**: 120 km
- **Delivery Mode**: Truck
- **Base Lead Time**: 1.5 hours

## How to Use
Send a message to inquire about inventory or request a quote:

**Example Messages:**
- "What supplies do you have available?"
- "Can you provide 200 blankets to Berkeley?"
- "Check inventory for medical supplies"
- "Quote for water and food supplies delivery to Oakland"

## Integration
Part of the AgentAid Disaster Response Platform
"""

print("=" * 80)
print("📦 AgentAid Supply Agent Registration")
print("=" * 80)
print(f"\nAgent Configuration:")
print(f"  Name: {name}")
print(f"  Address: {identity.address}")
print(f"  Endpoint: {AGENT_ENDPOINT}")
print(f"  Location: {SUPPLIER_LOCATION}")
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
print(f"Supplier Location: {SUPPLIER_LOCATION}")
print(f"Protocol: Chat Protocol + AidProtocol v2.0.0")
print("\n" + "=" * 80)

print("\n✅ Agent is ready for registration!")
print("\nMake sure your agent is running:")
print(f"  python agents/supply_agent_chat_adapter.py")
print(f"\nTest the endpoint:")
print(f"  curl {AGENT_ENDPOINT}/status")
print("\n" + "=" * 80)
