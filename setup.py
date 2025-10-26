#!/usr/bin/env python3
"""
AgentAid Setup Script
Install dependencies and set up environment
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")

    requirements_file = Path(__file__).parent / "requirements.txt"

    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False

    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_env_file():
    """Create .env file template"""
    print("📝 Creating .env file template...")

    env_file = Path(__file__).parent / ".env"

    if env_file.exists():
        print("⚠️ .env file already exists")
        return True

    env_content = """# AgentAid Environment Configuration

# Required: Anthropic Claude API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Geocoding service configuration
GEOCODING_PROVIDER=opencage  # or 'google'
OPENCAGE_API_KEY=your_opencage_key  # if using OpenCage
GOOGLE_MAPS_API_KEY=your_google_key  # if using Google Maps

# Optional: Service URLs
CLAUDE_SERVICE_URL=http://localhost:3000
TELEMETRY_URL=http://127.0.0.1:8088/ingest
"""

    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
        print("📝 Please edit .env file and add your API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")

    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        return False

    print(f"✅ Python version {sys.version.split()[0]} is compatible")
    return True

def main():
    """Main setup function"""
    print("🚨 AgentAid Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed at requirements installation")
        sys.exit(1)

    # Create .env file
    if not create_env_file():
        print("\n❌ Setup failed at .env file creation")
        sys.exit(1)

    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your ANTHROPIC_API_KEY")
    print("2. Run the demo: python demo.py")
    print("3. Start the app: python run_streamlit.py")
    print("\nFor more information, see README_STREAMLIT.md")

if __name__ == "__main__":
    main()
