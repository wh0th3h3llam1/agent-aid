#!/usr/bin/env python3
"""
Debug script to capture agent output and see why they're stopping
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_agent_with_output(name, command, cwd, env_vars=None):
    """Start an agent and capture its output"""
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
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        print(f"✅ {name} started (PID: {process.pid})")
        print(f"📝 Output from {name}:")
        print("-" * 50)
        
        # Read output line by line
        try:
            while True:
                line = process.stdout.readline()
                if line:
                    print(f"[{name}] {line.strip()}")
                elif process.poll() is not None:
                    # Process has ended
                    break
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(f"\n🛑 Stopping {name}...")
            process.terminate()
            process.wait()
            return None
        
        # Get any remaining output
        remaining_output = process.stdout.read()
        if remaining_output:
            print(f"[{name}] {remaining_output.strip()}")
        
        return_code = process.wait()
        print(f"📊 {name} exited with code: {return_code}")
        
        return process
        
    except Exception as e:
        print(f"❌ Error starting {name}: {e}")
        return None

def test_supply_agent():
    """Test supply agent with output capture"""
    print("🏥 Testing Supply Agent with Output Capture")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    marketplace_dir = base_dir / "agentaid-marketplace"
    
    env_vars = {
        "SUPPLIER_NAME": "emergency_medical_fire",
        "SUPPLIER_SEED": "emergency_medical_fire_demo_seed",
        "SUPPLIER_PORT": "8001",
        "SUPPLIER_LAT": "37.7749",
        "SUPPLIER_LON": "-122.4194",
        "SUPPLIER_LABEL": "Emergency Medical & Fire Response Depot",
        "SUPPLIER_LEAD_H": "1.0",
        "SUPPLIER_RADIUS_KM": "150.0",
        "SUPPLIER_DELIVERY_MODE": "ambulance"
    }
    
    process = start_agent_with_output(
        "Supply Agent",
        ["python", "agents/supply_agent.py"],
        marketplace_dir,
        env_vars
    )
    
    if process:
        print("✅ Supply agent test completed")
    else:
        print("❌ Supply agent test failed")

def test_need_agent():
    """Test need agent with output capture"""
    print("\n📋 Testing Need Agent with Output Capture")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    marketplace_dir = base_dir / "agentaid-marketplace"
    
    env_vars = {
        "NEEDER_NAME": "need_agent_berkeley_1",
        "NEEDER_SEED": "need_agent_berkeley_1_demo_seed",
        "NEEDER_PORT": "8000",
        "NEED_LAT": "37.8715",
        "NEED_LON": "-122.2730",
        "NEED_LABEL": "Berkeley Emergency Center",
        "NEED_PRIORITY": "critical",
        "NEED_ITEMS_JSON": '[{"name":"blanket","qty":200,"unit":"ea"}]'
    }
    
    process = start_agent_with_output(
        "Need Agent",
        ["python", "agents/need_agent.py"],
        marketplace_dir,
        env_vars
    )
    
    if process:
        print("✅ Need agent test completed")
    else:
        print("❌ Need agent test failed")

def main():
    """Main debug function"""
    print("🚨 AgentAid Agent Debug with Output Capture")
    print("=" * 60)
    print("This will show you exactly what's happening with each agent")
    print("Press Ctrl+C to stop each test")
    print("=" * 60)
    
    try:
        # Test supply agent
        test_supply_agent()
        
        # Wait a moment between tests
        time.sleep(2)
        
        # Test need agent
        test_need_agent()
        
    except KeyboardInterrupt:
        print("\n🛑 Debug session stopped by user")
    
    print("\n🎯 Debug complete!")
    print("Check the output above to see what's causing the agents to stop.")

if __name__ == "__main__":
    main()
