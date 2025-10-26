#!/usr/bin/env python3
"""
Simple test script to start agents and verify they're working
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_agent(name, command, cwd, env_vars=None):
    """Start a single agent and return the process"""
    print(f"🚀 Starting {name}...")
    
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(2)
        
        if process.poll() is None:
            print(f"✅ {name} started successfully (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {name} failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting {name}: {e}")
        return None

def test_individual_agents():
    """Test starting agents individually"""
    print("🧪 Testing Individual Agents")
    print("=" * 40)
    
    base_dir = Path(__file__).parent
    marketplace_dir = base_dir / "agentaid-marketplace"
    
    # Test supply agent first
    print("\n🏥 Testing Supply Agent...")
    supply_process = start_agent(
        "Supply Agent",
        ["python", "agents/supply_agent.py"],
        marketplace_dir,
        {
            "SUPPLIER_NAME": "test_supplier",
            "SUPPLIER_SEED": "test_supplier_seed",
            "SUPPLIER_PORT": "8001",
            "SUPPLIER_LAT": "37.78",
            "SUPPLIER_LON": "-122.42",
            "SUPPLIER_LABEL": "Test Supplier",
            "SUPPLIER_LEAD_H": "1.0",
            "SUPPLIER_RADIUS_KM": "100.0",
            "SUPPLIER_DELIVERY_MODE": "truck"
        }
    )
    
    if supply_process:
        print("✅ Supply agent is running")
        # Let it run for a few seconds
        time.sleep(5)
        supply_process.terminate()
        supply_process.wait()
        print("🛑 Supply agent stopped")
    else:
        print("❌ Supply agent failed")
        return False
    
    # Test need agent
    print("\n📋 Testing Need Agent...")
    need_process = start_agent(
        "Need Agent",
        ["python", "agents/need_agent.py"],
        marketplace_dir,
        {
            "NEEDER_NAME": "test_need_agent",
            "NEEDER_SEED": "test_need_agent_seed",
            "NEEDER_PORT": "8000",
            "NEED_LAT": "37.8715",
            "NEED_LON": "-122.2730",
            "NEED_LABEL": "Test Location",
            "NEED_PRIORITY": "critical",
            "NEED_ITEMS_JSON": '[{"name":"blanket","qty":200,"unit":"ea"}]'
        }
    )
    
    if need_process:
        print("✅ Need agent is running")
        # Let it run for a few seconds
        time.sleep(5)
        need_process.terminate()
        need_process.wait()
        print("🛑 Need agent stopped")
    else:
        print("❌ Need agent failed")
        return False
    
    return True

def test_claude_service():
    """Test if Claude service is working"""
    print("\n🤖 Testing Claude Service...")
    
    try:
        import requests
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Claude service is running")
            return True
        else:
            print(f"❌ Claude service returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Claude service not accessible: {e}")
        return False

def main():
    """Main test function"""
    print("🚨 AgentAid Agent Testing")
    print("=" * 50)
    
    # Test Claude service first
    if not test_claude_service():
        print("\n❌ Claude service is not running. Please start it first:")
        print("   python start_dummy_agents.py")
        return False
    
    # Test individual agents
    if test_individual_agents():
        print("\n🎉 All agents are working correctly!")
        print("\n💡 The issue might be with agent communication.")
        print("   Try starting the full system and check the logs.")
        return True
    else:
        print("\n❌ Some agents are failing. Check the error messages above.")
        return False

if __name__ == "__main__":
    main()
