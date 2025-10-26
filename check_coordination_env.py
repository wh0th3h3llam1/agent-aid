#!/usr/bin/env python3
"""
Check if coordination agent environment variables are set correctly
"""
import os
import sys
from pathlib import Path

# Simulate the coordination agent environment
sys.path.insert(0, str(Path(__file__).parent / "agentaid-marketplace"))

# Set the environment variables as they would be in start_agents_fixed.py
os.environ['NEED_AGENT_ADDRS'] = 'agent1qgw06us8yrrmnx40dq7vlm5vqyd25tv3qx3kyax9x5k2kz7kuguxjy4a8hu'
os.environ['SUPPLY_AGENT_ADDRS'] = 'agent1qvp9jjj2rjtnj5nhnrnvmnm856l8t6gs7uyjw9ucpunepz9fmvpr5r4q8q3,agent1qf4u39wdxxdpucmt2t49dr0jw80f9cqlyqwvhue8yrayg9hf7r08j8cd9mn'

# Now check what the coordination agent would read
NEED_AGENT_ADDRESSES = [a.strip() for a in os.getenv("NEED_AGENT_ADDRS", "").split(",") if a.strip()]
SUPPLY_AGENT_ADDRESSES = [a.strip() for a in os.getenv("SUPPLY_AGENT_ADDRS", "").split(",") if a.strip()]

print("🔍 Checking Coordination Agent Environment Variables\n")

print(f"NEED_AGENT_ADDRS env var: {os.getenv('NEED_AGENT_ADDRS', 'NOT SET')}")
print(f"SUPPLY_AGENT_ADDRS env var: {os.getenv('SUPPLY_AGENT_ADDRS', 'NOT SET')}\n")

print(f"Parsed NEED_AGENT_ADDRESSES: {NEED_AGENT_ADDRESSES}")
print(f"  Count: {len(NEED_AGENT_ADDRESSES)}\n")

print(f"Parsed SUPPLY_AGENT_ADDRESSES: {SUPPLY_AGENT_ADDRESSES}")
print(f"  Count: {len(SUPPLY_AGENT_ADDRESSES)}\n")

if NEED_AGENT_ADDRESSES and SUPPLY_AGENT_ADDRESSES:
    print("✅ Agent addresses are configured correctly!")
    print("\nAgent Registry would contain:")
    for addr in NEED_AGENT_ADDRESSES:
        print(f"  - Need Agent: {addr[:20]}...")
    for addr in SUPPLY_AGENT_ADDRESSES:
        print(f"  - Supply Agent: {addr[:20]}...")
else:
    print("❌ Agent addresses are NOT configured!")
    if not NEED_AGENT_ADDRESSES:
        print("  - Missing NEED_AGENT_ADDRESSES")
    if not SUPPLY_AGENT_ADDRESSES:
        print("  - Missing SUPPLY_AGENT_ADDRESSES")
