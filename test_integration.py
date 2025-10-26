#!/usr/bin/env python3
"""
AgentAid Integration Test Script
Tests the end-to-end workflow from UI input to agent coordination
"""

import requests
import json
import time
import sys
from pathlib import Path

class AgentAidTester:
    def __init__(self):
        self.claude_url = "http://localhost:3000"
        self.test_results = []
    
    def test_claude_service_health(self):
        """Test if Claude service is running"""
        print("🔍 Testing Claude service health...")
        try:
            response = requests.get(f"{self.claude_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Claude service is healthy")
                print(f"   Service: {data.get('service', 'Unknown')}")
                print(f"   Version: {data.get('version', 'Unknown')}")
                print(f"   Features: {data.get('features', {})}")
                return True
            else:
                print(f"❌ Claude service health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Claude service is not accessible: {e}")
            return False
    
    def test_disaster_extraction(self):
        """Test disaster data extraction"""
        print("\n🔍 Testing disaster data extraction...")
        
        test_inputs = [
            {
                "input": "We need 50 blankets and 100 water bottles at the community center. This is urgent! There are about 200 people affected. Contact: 555-1234",
                "expected_items": ["blankets", "water bottles"],
                "expected_priority": "high"
            },
            {
                "input": "Medical supplies needed at the hospital. Critical situation!",
                "expected_items": ["medical supplies"],
                "expected_priority": "critical"
            },
            {
                "input": "We need food and shelter at the school gymnasium. About 50 people here.",
                "expected_items": ["food", "shelter"],
                "expected_priority": "medium"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_inputs, 1):
            print(f"\n   Test Case {i}: {test_case['input'][:50]}...")
            
            try:
                response = requests.post(
                    f"{self.claude_url}/api/extract",
                    json={"input": test_case["input"], "source": "test"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        extracted_data = data.get("data", {})
                        items = extracted_data.get("items", [])
                        priority = extracted_data.get("priority", "")
                        
                        print(f"   ✅ Extraction successful")
                        print(f"      Items: {items}")
                        print(f"      Priority: {priority}")
                        print(f"      Location: {extracted_data.get('location', 'N/A')}")
                        
                        # Check if extraction meets expectations
                        items_match = any(
                            any(expected_item.lower() in item.lower() for expected_item in test_case["expected_items"])
                            for item in items
                        )
                        priority_match = test_case["expected_priority"] in priority.lower()
                        
                        if items_match and priority_match:
                            print(f"   ✅ Extraction quality: GOOD")
                            success_count += 1
                        else:
                            print(f"   ⚠️  Extraction quality: PARTIAL")
                            success_count += 0.5
                    else:
                        print(f"   ❌ Extraction failed: {data.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ HTTP error: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Request failed: {e}")
        
        success_rate = (success_count / len(test_inputs)) * 100
        print(f"\n📊 Extraction Test Results: {success_rate:.1f}% success rate")
        return success_rate >= 70
    
    def test_agent_endpoints(self):
        """Test agent-related endpoints"""
        print("\n🔍 Testing agent endpoints...")
        
        endpoints = [
            ("/api/uagent/pending-requests", "GET", "Pending requests"),
            ("/api/requests", "GET", "All requests"),
            ("/api/stats", "GET", "System statistics")
        ]
        
        success_count = 0
        
        for endpoint, method, description in endpoints:
            print(f"   Testing {description}...")
            
            try:
                if method == "GET":
                    response = requests.get(f"{self.claude_url}{endpoint}", timeout=10)
                else:
                    response = requests.post(f"{self.claude_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", True):  # Some endpoints don't have success field
                        print(f"   ✅ {description}: OK")
                        success_count += 1
                    else:
                        print(f"   ⚠️  {description}: {data.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ {description}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {description}: {e}")
        
        success_rate = (success_count / len(endpoints)) * 100
        print(f"\n📊 Agent Endpoints Test: {success_rate:.1f}% success rate")
        return success_rate >= 66
    
    def test_geocoding(self):
        """Test geocoding functionality"""
        print("\n🔍 Testing geocoding...")
        
        test_addresses = [
            "123 Main Street, Berkeley, CA",
            "San Francisco General Hospital, San Francisco, CA",
            "Oakland Coliseum, Oakland, CA"
        ]
        
        success_count = 0
        
        for address in test_addresses:
            print(f"   Geocoding: {address}")
            
            try:
                response = requests.post(
                    f"{self.claude_url}/api/geocode",
                    json={"address": address},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("geocoded"):
                        coords = data["geocoded"]
                        print(f"   ✅ Coordinates: {coords.get('latitude')}, {coords.get('longitude')}")
                        success_count += 1
                    else:
                        print(f"   ⚠️  Could not geocode: {address}")
                else:
                    print(f"   ❌ HTTP error: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Geocoding failed: {e}")
        
        success_rate = (success_count / len(test_addresses)) * 100
        print(f"\n📊 Geocoding Test: {success_rate:.1f}% success rate")
        return success_rate >= 66
    
    def test_full_workflow(self):
        """Test the complete workflow from input to agent processing"""
        print("\n🔍 Testing full workflow...")
        
        # Submit a disaster request
        disaster_input = "We need emergency medical supplies at the hospital. This is critical! Contact: 555-EMERGENCY"
        
        print(f"   Submitting request: {disaster_input}")
        
        try:
            # Submit the request
            response = requests.post(
                f"{self.claude_url}/api/extract",
                json={"input": disaster_input, "source": "integration_test"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and not data.get("needs_followup"):
                    request_data = data.get("data", {})
                    request_id = request_data.get("request_id")
                    
                    print(f"   ✅ Request submitted: {request_id}")
                    print(f"   Priority: {request_data.get('priority', 'unknown')}")
                    print(f"   Items: {request_data.get('items', [])}")
                    
                    # Wait a moment for processing
                    print("   ⏳ Waiting for agent processing...")
                    time.sleep(3)
                    
                    # Check if request is available for agents
                    pending_response = requests.get(f"{self.claude_url}/api/uagent/pending-requests")
                    if pending_response.status_code == 200:
                        pending_data = pending_response.json()
                        pending_requests = pending_data.get("requests", [])
                        
                        # Check if our request is in the pending list
                        our_request = next(
                            (req for req in pending_requests if req.get("request_id") == request_id),
                            None
                        )
                        
                        if our_request:
                            print(f"   ✅ Request available for agents")
                            print(f"   Status: {our_request.get('status', 'unknown')}")
                            return True
                        else:
                            print(f"   ⚠️  Request not found in pending list")
                            return False
                    else:
                        print(f"   ❌ Could not check pending requests")
                        return False
                else:
                    print(f"   ❌ Request submission failed or needs follow-up")
                    return False
            else:
                print(f"   ❌ HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Workflow test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚨 AgentAid Integration Test Suite")
        print("=" * 50)
        
        tests = [
            ("Claude Service Health", self.test_claude_service_health),
            ("Disaster Extraction", self.test_disaster_extraction),
            ("Agent Endpoints", self.test_agent_endpoints),
            ("Geocoding", self.test_geocoding),
            ("Full Workflow", self.test_full_workflow)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if test_func():
                    print(f"✅ {test_name}: PASSED")
                    passed_tests += 1
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
        
        # Summary
        print(f"\n{'='*50}")
        print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! AgentAid is ready for use.")
            return True
        elif passed_tests >= total_tests * 0.8:
            print("⚠️  Most tests passed. System is mostly functional.")
            return True
        else:
            print("❌ Multiple test failures. Please check the setup.")
            return False

def main():
    """Main test function"""
    print("Starting AgentAid integration tests...")
    
    # Check if we're in the right directory
    if not Path("agentaid-claude-service").exists():
        print("❌ Please run this script from the agent-aid root directory")
        sys.exit(1)
    
    # Run tests
    tester = AgentAidTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Ready to start AgentAid!")
        print("Run: python start_agentaid.py")
        print("Then visit: http://localhost:3000/disaster-response.html")
        sys.exit(0)
    else:
        print("\n🔧 Please fix the issues above before running AgentAid")
        sys.exit(1)

if __name__ == "__main__":
    main()
