#!/usr/bin/env python3
"""
AgentAid Streamlit Application Runner
Simple startup script with environment setup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['ANTHROPIC_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables and try again.")
        print("Example:")
        print("   export ANTHROPIC_API_KEY=your_api_key_here")
        return False

    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import streamlit
        import anthropic
        import requests
        import numpy
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements:")
        print("   pip install -r requirements.txt")
        return False

def main():
    """Main entry point"""
    print("🚨 AgentAid Streamlit Application")
    print("=" * 50)

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Get the directory of this script
    script_dir = Path(__file__).parent
    streamlit_app = script_dir / "streamlit_app.py"

    if not streamlit_app.exists():
        print(f"❌ Streamlit app not found: {streamlit_app}")
        sys.exit(1)

    print("✅ Environment check passed")
    print("🚀 Starting Streamlit application...")
    print("📱 Application will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)

    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(streamlit_app),
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
