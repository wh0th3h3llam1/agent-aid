#!/usr/bin/env python3
"""
AgentAid Setup Script
Installs dependencies and sets up the disaster response platform
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_node_dependencies():
    """Install Node.js dependencies for Claude service"""
    claude_dir = Path("agentaid-claude-service")
    if not claude_dir.exists():
        print("❌ Claude service directory not found")
        return False
    
    os.chdir(claude_dir)
    
    # Check if package.json exists
    if not Path("package.json").exists():
        print("❌ package.json not found in Claude service directory")
        return False
    
    # Install dependencies
    if not run_command("npm install", "Installing Node.js dependencies"):
        return False
    
    os.chdir("..")
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    requirements_files = [
        "agentaid-marketplace/requirements.txt"
    ]
    
    for req_file in requirements_files:
        if Path(req_file).exists():
            if not run_command(f"pip install -r {req_file}", f"Installing Python dependencies from {req_file}"):
                return False
    
    # Install additional dependencies
    additional_deps = [
        "requests",
        "httpx"
    ]
    
    for dep in additional_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    return True

def setup_database():
    """Set up the database"""
    marketplace_dir = Path("agentaid-marketplace")
    if not marketplace_dir.exists():
        print("❌ Marketplace directory not found")
        return False
    
    os.chdir(marketplace_dir)
    
    # Check if database exists
    db_path = Path("db/agent_aid.db")
    if not db_path.exists():
        print("📊 Setting up database...")
        # The database will be created when the agents start
        print("✅ Database will be created on first run")
    else:
        print("✅ Database already exists")
    
    os.chdir("..")
    return True

def create_env_files():
    """Create environment files with default values"""
    env_files = [
        {
            "path": "agentaid-claude-service/.env",
            "content": """# Claude Service Environment Variables
ANTHROPIC_API_KEY=your_anthropic_api_key_here
PORT=3000
NODE_ENV=development
"""
        },
        {
            "path": "agentaid-marketplace/.env",
            "content": """# AgentAid Marketplace Environment Variables
TELEMETRY_URL=http://127.0.0.1:8088/ingest
INV_DB_PATH=db/agent_aid.db

# Coordination Agent
COORDINATOR_NAME=coordination_agent_1
COORDINATOR_SEED=coordination_agent_1_demo_seed
COORDINATOR_PORT=8002
CLAUDE_SERVICE_URL=http://localhost:3000

# Need Agent
NEEDER_NAME=need_agent_berkeley_1
NEEDER_SEED=need_agent_berkeley_1_demo_seed
NEEDER_PORT=8000
NEED_LAT=37.8715
NEED_LON=-122.2730
NEED_LABEL=Berkeley Emergency Center
NEED_PRIORITY=critical
NEED_ITEMS_JSON=[{"name":"blanket","qty":200,"unit":"ea"}]

# Supply Agent 1
SUPPLIER_NAME=supply_sf_store_1
SUPPLIER_SEED=supply_sf_store_1_demo_seed
SUPPLIER_PORT=8001
SUPPLIER_LAT=37.78
SUPPLIER_LON=-122.42
SUPPLIER_LABEL=SF Depot
SUPPLIER_LEAD_H=1.5
SUPPLIER_RADIUS_KM=120.0
SUPPLIER_DELIVERY_MODE=truck

# Supply Agent 2
SUPPLIER_NAME_2=supply_oakland_store_2
SUPPLIER_SEED_2=supply_oakland_store_2_demo_seed
SUPPLIER_PORT_2=8003
SUPPLIER_LAT_2=37.8044
SUPPLIER_LON_2=-122.2712
SUPPLIER_LABEL_2=Oakland Depot
SUPPLIER_LEAD_H_2=2.0
SUPPLIER_RADIUS_KM_2=100.0
SUPPLIER_DELIVERY_MODE_2=van
"""
        }
    ]
    
    for env_file in env_files:
        if not Path(env_file["path"]).exists():
            with open(env_file["path"], "w") as f:
                f.write(env_file["content"])
            print(f"✅ Created {env_file['path']}")
        else:
            print(f"✅ {env_file['path']} already exists")

def main():
    """Main setup function"""
    print("🚨 AgentAid Disaster Response Platform Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    if not install_node_dependencies():
        print("❌ Failed to install Node.js dependencies")
        sys.exit(1)
    
    # Set up database
    print("\n📊 Setting up database...")
    if not setup_database():
        print("❌ Failed to set up database")
        sys.exit(1)
    
    # Create environment files
    print("\n⚙️  Creating environment files...")
    create_env_files()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Add your Anthropic API key to agentaid-claude-service/.env")
    print("2. Run: python start_agentaid.py")
    print("3. Open: http://localhost:3000/disaster-response.html")
    
    print("\n🔧 Manual setup (if needed):")
    print("- Install Node.js 18+ and npm")
    print("- Install Python 3.8+ and pip")
    print("- Get Anthropic API key from https://console.anthropic.com/")

if __name__ == "__main__":
    main()
