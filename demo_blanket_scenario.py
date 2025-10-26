#!/usr/bin/env python3
"""
AgentAid Demo: Blanket Request Scenario
Demonstrates how the system coordinates between suppliers to fulfill a 100-blanket request
"""

import requests
import json
import time
import sys
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🚨 {title}")
    print(f"{'='*60}")

def print_step(step_num, title, description=""):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}: {title}")
    if description:
        print(f"   {description}")

def demo_blanket_scenario():
    """Demonstrate the complete blanket request scenario"""
    
    print_header("AgentAid Demo: Blanket Request Coordination")
    
    print("🎯 Scenario: User needs 100 blankets at community center")
    print("🤖 System: Coordinates between two suppliers to fulfill request")
    
    # Step 1: Show supplier inventory
    print_step(1, "Supplier Inventory Setup", "Two suppliers with different inventory")
    
    print("\n🏥 Emergency Medical & Fire Response Depot:")
    print("   📦 500 blankets @ $25.00 each")
    print("   🚑 10 ambulances @ $50,000.00 each") 
    print("   💊 200 burn medicine bottles @ $45.00 each")
    print("   📍 Location: San Francisco")
    print("   🚚 Delivery: Ambulance (1h lead time)")
    
    print("\n👶 Family & Child Emergency Supplies:")
    print("   📦 50 blankets @ $20.00 each")
    print("   👶 10 emergency baby food cases @ $35.00 each")
    print("   🍼 20 diaper packs @ $25.00 each")
    print("   📍 Location: Oakland")
    print("   🚚 Delivery: Van (1.5h lead time)")
    
    # Step 2: User submits request
    print_step(2, "User Submits Request", "Natural language disaster report")
    
    user_input = "We need 100 blankets at the community center. This is urgent! There are about 200 people affected. Contact: 555-EMERGENCY"
    print(f"📝 User Input: '{user_input}'")
    
    # Step 3: Claude processes request
    print_step(3, "Claude AI Processing", "Extracts structured data from natural language")
    
    print("🤖 Claude extracts:")
    print("   📋 Items: ['blankets']")
    print("   🔢 Quantity: 100")
    print("   📍 Location: 'community center'")
    print("   ⚡ Priority: 'urgent' → 'high'")
    print("   👥 Victim Count: 200")
    print("   📞 Contact: 555-EMERGENCY")
    
    # Step 4: Coordination agent assigns
    print_step(4, "Coordination Agent Assignment", "Routes request to appropriate agents")
    
    print("🎯 Coordination Agent:")
    print("   📊 Analyzes request: 100 blankets needed")
    print("   🤖 Assigns to Need Agent for priority evaluation")
    print("   📋 Creates quote request for suppliers")
    print("   🔄 Monitors agent responses")
    
    # Step 5: Need agent evaluates
    print_step(5, "Need Agent Evaluation", "Assesses priority and requirements")
    
    print("📊 Need Agent:")
    print("   ⚡ Priority: HIGH (urgent request)")
    print("   👥 Affected: 200 people")
    print("   📍 Location: Community center")
    print("   🎯 Decision: Request valid, send to suppliers")
    
    # Step 6: Supply agents respond
    print_step(6, "Supply Agent Responses", "Both suppliers provide quotes")
    
    print("🏥 Emergency Medical Supplier:")
    print("   ✅ Can provide: 100 blankets")
    print("   💰 Cost: $2,500.00 (100 × $25.00)")
    print("   ⏱️  ETA: 1.5 hours (1h lead + 0.5h travel)")
    print("   📦 Coverage: 100% of request")
    print("   🚚 Delivery: Ambulance")
    
    print("\n👶 Family & Child Supplier:")
    print("   ✅ Can provide: 50 blankets")
    print("   💰 Cost: $1,000.00 (50 × $20.00)")
    print("   ⏱️  ETA: 2.0 hours (1.5h lead + 0.5h travel)")
    print("   📦 Coverage: 50% of request")
    print("   🚚 Delivery: Van")
    
    # Step 7: Coordination and allocation
    print_step(7, "Coordination & Allocation", "System selects optimal supplier combination")
    
    print("🤝 Coordination Agent Decision:")
    print("   📊 Analysis:")
    print("      • Emergency Medical: 100% coverage, faster delivery")
    print("      • Family & Child: 50% coverage, slower delivery")
    print("      • Combined: 150% coverage (over-fulfillment possible)")
    
    print("\n   🎯 Optimal Allocation:")
    print("      • Primary: Emergency Medical (100 blankets)")
    print("      • Backup: Family & Child (50 blankets) - if needed")
    print("      • Result: 100 blankets confirmed from Emergency Medical")
    
    # Step 8: Final confirmation
    print_step(8, "Final Confirmation", "Request fulfilled and confirmed")
    
    print("✅ Allocation Confirmed:")
    print("   🏥 Emergency Medical & Fire Response Depot")
    print("   📦 100 blankets allocated")
    print("   💰 Total cost: $2,500.00")
    print("   ⏱️  Delivery ETA: 1.5 hours")
    print("   📍 Destination: Community center")
    print("   🚚 Delivery method: Ambulance")
    
    print("\n📊 System Benefits Demonstrated:")
    print("   ✅ Multiple suppliers coordinated")
    print("   ✅ Geographic optimization (closest supplier selected)")
    print("   ✅ Inventory management (prevents over-allocation)")
    print("   ✅ Real-time coordination between AI agents")
    print("   ✅ Cost optimization (best price selected)")
    print("   ✅ Delivery optimization (fastest delivery selected)")
    
    print("\n🎉 Scenario Complete!")
    print("The system successfully coordinated between suppliers to fulfill the 100-blanket request!")

def test_real_api():
    """Test the actual API if services are running"""
    print_header("Testing Real API Integration")
    
    claude_url = "http://localhost:3000"
    
    try:
        # Test health
        print("🔍 Testing Claude service health...")
        response = requests.get(f"{claude_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Claude service is running")
            
            # Test blanket request
            print("\n🧪 Testing blanket request...")
            test_input = "We need 100 blankets at the community center. This is urgent!"
            
            response = requests.post(
                f"{claude_url}/api/extract",
                json={"input": test_input, "source": "demo"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Request processed successfully!")
                    print(f"   Items: {data.get('data', {}).get('items', [])}")
                    print(f"   Priority: {data.get('data', {}).get('priority', 'unknown')}")
                    return True
                else:
                    print("❌ Request processing failed")
                    return False
            else:
                print(f"❌ API error: {response.status_code}")
                return False
        else:
            print("❌ Claude service not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure to start the services first:")
        print("   python start_dummy_agents.py")
        return False

def main():
    """Main demo function"""
    print("🚨 AgentAid Blanket Request Demo")
    print("Demonstrating AI agent coordination for disaster response")
    
    # Show the complete scenario
    demo_blanket_scenario()
    
    # Test real API if available
    print_header("Real API Test")
    if test_real_api():
        print("\n🎉 Demo completed successfully!")
        print("The system is ready for real disaster response coordination!")
    else:
        print("\n💡 To test with real agents:")
        print("1. Run: python start_dummy_agents.py")
        print("2. Open: http://localhost:3000/disaster-response.html")
        print("3. Submit: 'We need 100 blankets at the community center'")

if __name__ == "__main__":
    main()
