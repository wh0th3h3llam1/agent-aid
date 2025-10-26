#!/usr/bin/env python3
"""
Debug script to check why agents are stopping
"""

import subprocess
import sys
import os
from pathlib import Path

def test_agent_startup():
    """Test individual agent startup to identify issues"""
    
    print("🔍 Debugging Agent Startup Issues")
    print("=" * 50)
    
    # Test database initialization
    print("\n📊 Testing database initialization...")
    try:
        result = subprocess.run([
            sys.executable, 
            str(Path("agentaid-marketplace/db/init_db.py"))
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ Database initialization: OK")
        else:
            print(f"❌ Database initialization failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False
    
    # Test dummy suppliers setup
    print("\n🏥 Testing dummy suppliers setup...")
    try:
        result = subprocess.run([
            sys.executable, 
            str(Path("agentaid-marketplace/db/setup_dummy_suppliers.py"))
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ Dummy suppliers setup: OK")
            print(result.stdout)
        else:
            print(f"❌ Dummy suppliers setup failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Dummy suppliers setup error: {e}")
        return False
    
    # Test individual agent startup
    agents_to_test = [
        {
            "name": "Need Agent",
            "path": Path("agentaid-marketplace"),
            "command": ["python", "agents/need_agent.py"],
            "env": {
                "NEEDER_NAME": "test_need_agent",
                "NEEDER_SEED": "test_need_agent_seed",
                "NEEDER_PORT": "8000",
                "NEED_LAT": "37.8715",
                "NEED_LON": "-122.2730",
                "NEED_LABEL": "Test Location",
                "NEED_PRIORITY": "critical",
                "NEED_ITEMS_JSON": '[{"name":"blanket","qty":200,"unit":"ea"}]'
            }
        },
        {
            "name": "Supply Agent",
            "path": Path("agentaid-marketplace"),
            "command": ["python", "agents/supply_agent.py"],
            "env": {
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
        }
    ]
    
    for agent in agents_to_test:
        print(f"\n🤖 Testing {agent['name']}...")
        
        try:
            # Set up environment
            env = os.environ.copy()
            env.update(agent['env'])
            
            # Start the agent
            process = subprocess.Popen(
                agent['command'],
                cwd=agent['path'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment to see if it starts
            import time
            time.sleep(3)
            
            # Check if it's still running
            if process.poll() is None:
                print(f"✅ {agent['name']}: Started successfully")
                process.terminate()
                process.wait()
            else:
                print(f"❌ {agent['name']}: Stopped immediately")
                stdout, stderr = process.communicate()
                print(f"   STDOUT: {stdout}")
                print(f"   STDERR: {stderr}")
                
        except Exception as e:
            print(f"❌ {agent['name']}: Error - {e}")
    
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        "uagents",
        "requests", 
        "httpx",
        "anthropic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main debug function"""
    print("🚨 AgentAid Debug Script")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install them first.")
        return
    
    # Test agent startup
    test_agent_startup()
    
    print("\n🎯 Debug complete!")
    print("If agents are still stopping, check the error messages above.")

if __name__ == "__main__":
    main()
