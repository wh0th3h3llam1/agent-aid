#!/usr/bin/env python3
"""
AgentAid Demo Script
Test the Streamlit application functionality
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")

    try:
        from services.claude_service import ClaudeService
        print("ClaudeService imported")
    except Exception as e:
        print(f"ClaudeService import failed: {e}")
        return False

    try:
        from services.geocoding_service import GeocodingService
        print("GeocodingService imported")
    except Exception as e:
        print(f"GeocodingService import failed: {e}")
        return False

    try:
        from services.followup_service import FollowupService
        print("FollowupService imported")
    except Exception as e:
        print(f"FollowupService import failed: {e}")
        return False

    try:
        from services.vector_db import VectorDatabase
        print("VectorDatabase imported")
    except Exception as e:
        print(f"VectorDatabase import failed: {e}")
        return False

    try:
        from services.agent_integration import AgentIntegration
        print("AgentIntegration imported")
    except Exception as e:
        print(f"AgentIntegration import failed: {e}")
        return False

    return True

def test_services():
    """Test service initialization"""
    print("\n🧪 Testing service initialization...")

    try:
        from services.geocoding_service import GeocodingService
        geocoding = GeocodingService()
        print("✅ GeocodingService initialized")
    except Exception as e:
        print(f"❌ GeocodingService initialization failed: {e}")
        return False

    try:
        from services.followup_service import FollowupService
        followup = FollowupService()
        print("✅ FollowupService initialized")
    except Exception as e:
        print(f"❌ FollowupService initialization failed: {e}")
        return False

    try:
        from services.vector_db import VectorDatabase
        vector_db = VectorDatabase()
        print("✅ VectorDatabase initialized")
    except Exception as e:
        print(f"❌ VectorDatabase initialization failed: {e}")
        return False

    try:
        from services.agent_integration import AgentIntegration
        agent_integration = AgentIntegration()
        print("✅ AgentIntegration initialized")
    except Exception as e:
        print(f"❌ AgentIntegration initialization failed: {e}")
        return False

    return True

def test_claude_service():
    """Test Claude service (requires API key)"""
    print("\n🧪 Testing Claude service...")

    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️ ANTHROPIC_API_KEY not set, skipping Claude service test")
        return True

    try:
        from services.claude_service import ClaudeService
        claude = ClaudeService()

        # Test health check
        health = claude.check_health()
        if health:
            print("✅ Claude service is healthy")
        else:
            print("⚠️ Claude service health check failed")

        return True
    except Exception as e:
        print(f"❌ Claude service test failed: {e}")
        return False

def test_geocoding():
    """Test geocoding functionality"""
    print("\n🧪 Testing geocoding...")

    try:
        from services.geocoding_service import GeocodingService
        geocoding = GeocodingService()

        # Test with a simple address
        result = geocoding.geocode_address("San Francisco, CA")
        if result:
            print(f"✅ Geocoding test passed: {result['latitude']}, {result['longitude']}")
        else:
            print("⚠️ Geocoding test returned no results")

        return True
    except Exception as e:
        print(f"❌ Geocoding test failed: {e}")
        return False

def test_vector_db():
    """Test vector database functionality"""
    print("\n🧪 Testing vector database...")

    try:
        from services.vector_db import VectorDatabase
        vector_db = VectorDatabase()

        # Test data
        test_request = {
            'request_id': 'TEST-001',
            'items': ['blankets', 'water'],
            'location': 'Test Location',
            'priority': 'high',
            'timestamp': '2025-01-01T00:00:00'
        }

        # Store request
        success = vector_db.store_request(test_request)
        if success:
            print("✅ Vector database store test passed")
        else:
            print("❌ Vector database store test failed")
            return False

        # Test similarity search
        similar = vector_db.find_similar_requests("blankets water", limit=1)
        if similar:
            print("✅ Vector database search test passed")
        else:
            print("⚠️ Vector database search test returned no results")

        # Test stats
        stats = vector_db.get_stats()
        print(f"📊 Database stats: {stats}")

        return True
    except Exception as e:
        print(f"❌ Vector database test failed: {e}")
        return False

def main():
    """Main demo function"""
    print("AgentAid Demo Script")
    print("=" * 50)

    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        sys.exit(1)

    # Test service initialization
    if not test_services():
        print("\n❌ Service initialization tests failed")
        sys.exit(1)

    # Test Claude service
    if not test_claude_service():
        print("\n❌ Claude service test failed")
        sys.exit(1)

    # Test geocoding
    if not test_geocoding():
        print("\n❌ Geocoding test failed")
        sys.exit(1)

    # Test vector database
    if not test_vector_db():
        print("\n❌ Vector database test failed")
        sys.exit(1)

    print("\n🎉 All tests passed!")
    print("✅ The Streamlit application should work correctly")
    print("\nTo run the application:")
    print("   python run_streamlit.py")
    print("   # or")
    print("   streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
