#!/usr/bin/env python3
"""
Run coordination agent with visible output to debug
"""
import os
import sys
import subprocess
from pathlib import Path

# Set environment variables
env = os.environ.copy()
env['COORDINATOR_NAME'] = 'coordination_agent_1'
env['COORDINATOR_SEED'] = 'coordination_agent_1_demo_seed'
env['COORDINATOR_PORT'] = '8888'  # Use different port to avoid conflict
env['CLAUDE_SERVICE_URL'] = 'http://localhost:3000'
env['NEED_AGENT_ADDRS'] = 'agent1qgw06us8yrrmnx40dq7vlm5vqyd25tv3qx3kyax9x5k2kz7kuguxjy4a8hu'
env['SUPPLY_AGENT_ADDRS'] = 'agent1qvp9jjj2rjtnj5nhnrnvmnm856l8t6gs7uyjw9ucpunepz9fmvpr5r4q8q3,agent1qf4u39wdxxdpucmt2t49dr0jw80f9cqlyqwvhue8yrayg9hf7r08j8cd9mn'

print("🔍 Starting coordination agent with debug output...")
print(f"NEED_AGENT_ADDRS: {env['NEED_AGENT_ADDRS'][:50]}...")
print(f"SUPPLY_AGENT_ADDRS: {env['SUPPLY_AGENT_ADDRS'][:50]}...")
print("\n" + "="*60)
print("Agent output:")
print("="*60 + "\n")

# Change to marketplace directory
os.chdir(Path(__file__).parent / 'agentaid-marketplace')

# Run the coordination agent
try:
    subprocess.run(
        ['python', 'agents/coordination_agent.py'],
        env=env,
        timeout=30  # Run for 30 seconds
    )
except subprocess.TimeoutExpired:
    print("\n" + "="*60)
    print("Stopped after 30 seconds")
except KeyboardInterrupt:
    print("\n" + "="*60)
    print("Stopped by user")
