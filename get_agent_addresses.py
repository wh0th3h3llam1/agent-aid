#!/usr/bin/env python3
"""
Calculate agent addresses from their seeds
Agent addresses are deterministically generated from seeds
"""
from uagents import Agent

def get_agent_address(name: str, seed: str, port: int) -> str:
    """Get the address for an agent given its configuration"""
    # Create a temporary agent to get its address
    temp_agent = Agent(name=name, seed=seed, port=port)
    return str(temp_agent.address)

if __name__ == "__main__":
    # Define agent configurations (must match start_agents_fixed.py)
    agents = {
        "supply_agent_emergency": {
            "name": "emergency_medical_fire",
            "seed": "emergency_medical_fire_demo_seed",
            "port": 8001
        },
        "supply_agent_family": {
            "name": "family_child_emergency",
            "seed": "family_child_emergency_demo_seed",
            "port": 8003
        },
        "need_agent": {
            "name": "need_agent_berkeley_1",
            "seed": "need_agent_berkeley_1_demo_seed",
            "port": 8000
        },
        "coordination_agent": {
            "name": "coordination_agent_1",
            "seed": "coordination_agent_1_demo_seed",
            "port": 8002
        }
    }
    
    print("🔍 Calculating agent addresses from seeds...\n")
    
    addresses = {}
    for agent_key, config in agents.items():
        address = get_agent_address(config["name"], config["seed"], config["port"])
        addresses[agent_key] = address
        print(f"✅ {agent_key}:")
        print(f"   Name: {config['name']}")
        print(f"   Address: {address}\n")
    
    # Print environment variable format
    print("\n📋 Environment Variables for Agent Communication:\n")
    
    supply_addrs = f"{addresses['supply_agent_emergency']},{addresses['supply_agent_family']}"
    need_addrs = addresses['need_agent']
    
    print(f"SUPPLY_ADDRS={supply_addrs}")
    print(f"NEED_AGENT_ADDRS={need_addrs}")
    print(f"SUPPLY_AGENT_ADDRS={supply_addrs}")
    
    print("\n✅ Agent addresses calculated successfully!")
