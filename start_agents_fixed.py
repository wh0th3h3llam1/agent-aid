#!/usr/bin/env python3
"""
Fixed AgentAid startup script that handles port conflicts and agent communication
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

class FixedAgentAidOrchestrator:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        
        # First, set up the dummy suppliers
        self.setup_dummy_suppliers()
        
        self.services = {
            'claude_service': {
                'path': self.base_dir / 'agentaid-claude-service',
                'command': ['node', 'server.js'],
                'port': 3000,
                'health_url': 'http://localhost:3000/health',
                'startup_time': 5
            },
            'supply_agent_emergency': {
                'path': self.base_dir / 'agentaid-marketplace',
                'command': ['python', 'agents/supply_agent.py'],
                'port': 8001,
                'env_vars': {
                    'SUPPLIER_NAME': 'emergency_medical_fire',
                    'SUPPLIER_SEED': 'emergency_medical_fire_demo_seed',
                    'SUPPLIER_PORT': '8001',
                    'SUPPLIER_LAT': '37.7749',
                    'SUPPLIER_LON': '-122.4194',
                    'SUPPLIER_LABEL': 'Emergency Medical & Fire Response Depot',
                    'SUPPLIER_LEAD_H': '1.0',
                    'SUPPLIER_RADIUS_KM': '150.0',
                    'SUPPLIER_DELIVERY_MODE': 'ambulance'
                }
            },
            'supply_agent_family': {
                'path': self.base_dir / 'agentaid-marketplace',
                'command': ['python', 'agents/supply_agent.py'],
                'port': 8003,
                'env_vars': {
                    'SUPPLIER_NAME': 'family_child_emergency',
                    'SUPPLIER_SEED': 'family_child_emergency_demo_seed',
                    'SUPPLIER_PORT': '8003',
                    'SUPPLIER_LAT': '37.8044',
                    'SUPPLIER_LON': '-122.2712',
                    'SUPPLIER_LABEL': 'Family & Child Emergency Supplies Depot',
                    'SUPPLIER_LEAD_H': '1.5',
                    'SUPPLIER_RADIUS_KM': '120.0',
                    'SUPPLIER_DELIVERY_MODE': 'van'
                }
            },
            'need_agent': {
                'path': self.base_dir / 'agentaid-marketplace',
                'command': ['python', 'agents/need_agent.py'],
                'port': 8000,
                'env_vars': {
                    'NEEDER_NAME': 'need_agent_berkeley_1',
                    'NEEDER_SEED': 'need_agent_berkeley_1_demo_seed',
                    'NEEDER_PORT': '8000',
                    'NEED_LAT': '37.8715',
                    'NEED_LON': '-122.2730',
                    'NEED_LABEL': 'Berkeley Emergency Center',
                    'NEED_PRIORITY': 'critical',
                    'NEED_ITEMS_JSON': '[{"name":"blanket","qty":200,"unit":"ea"}]',
                    # Supply agent addresses (deterministically generated from seeds)
                    'SUPPLY_ADDRS': 'agent1qvp9jjj2rjtnj5nhnrnvmnm856l8t6gs7uyjw9ucpunepz9fmvpr5r4q8q3,agent1qf4u39wdxxdpucmt2t49dr0jw80f9cqlyqwvhue8yrayg9hf7r08j8cd9mn'
                }
            },
            'coordination_agent': {
                'path': self.base_dir / 'agentaid-marketplace',
                'command': ['python', 'agents/coordination_agent.py'],
                'port': 8002,
                'env_vars': {
                    'COORDINATOR_NAME': 'coordination_agent_1',
                    'COORDINATOR_SEED': 'coordination_agent_1_demo_seed',
                    'COORDINATOR_PORT': '8002',
                    'CLAUDE_SERVICE_URL': 'http://localhost:3000',
                    # Agent addresses for coordination
                    'NEED_AGENT_ADDRS': 'agent1qgw06us8yrrmnx40dq7vlm5vqyd25tv3qx3kyax9x5k2kz7kuguxjy4a8hu',
                    'SUPPLY_AGENT_ADDRS': 'agent1qvp9jjj2rjtnj5nhnrnvmnm856l8t6gs7uyjw9ucpunepz9fmvpr5r4q8q3,agent1qf4u39wdxxdpucmt2t49dr0jw80f9cqlyqwvhue8yrayg9hf7r08j8cd9mn'
                }
            }
        }
    
    def setup_dummy_suppliers(self):
        """Set up dummy suppliers with inventory"""
        print("🏥 Setting up dummy suppliers...")
        
        try:
            # Run the dummy supplier setup script
            result = subprocess.run([
                sys.executable, 
                str(self.base_dir / 'agentaid-marketplace' / 'db' / 'setup_dummy_suppliers.py')
            ], capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                print("✅ Dummy suppliers setup complete")
            else:
                print("❌ Failed to setup dummy suppliers")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error setting up dummy suppliers: {e}")
            return False
        
        return True
    
    def kill_existing_processes(self):
        """Kill any existing processes on the ports we need"""
        print("🧹 Cleaning up existing processes...")
        
        ports_to_check = [3000, 8000, 8001, 8002, 8003]
        
        for port in ports_to_check:
            try:
                # Find processes using the port
                result = subprocess.run(
                    f"lsof -ti :{port}",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            subprocess.run(f"kill -9 {pid}", shell=True)
                            print(f"   🔪 Killed process {pid} on port {port}")
                        except:
                            pass
            except:
                pass
        
        time.sleep(2)  # Give processes time to die
    
    def start_service(self, service_name, service_config):
        """Start a single service with better error handling"""
        print(f"\n🚀 Starting {service_name}...")
        
        # Set up environment variables
        env = os.environ.copy()
        if 'env_vars' in service_config:
            env.update(service_config['env_vars'])
        
        # Change to service directory
        os.chdir(service_config['path'])
        
        try:
            # Start the process
            process = subprocess.Popen(
                service_config['command'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment to see if it starts successfully
            time.sleep(3)
            
            if process.poll() is None:
                print(f"✅ {service_name} started (PID: {process.pid})")
                
                self.processes.append({
                    'name': service_name,
                    'process': process,
                    'config': service_config
                })
                
                # Wait for startup if specified
                if 'startup_time' in service_config:
                    time.sleep(service_config['startup_time'])
                
                return True
            else:
                # Process died immediately, get the error
                stdout, stderr = process.communicate()
                print(f"❌ {service_name} failed to start")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
            
        except Exception as e:
            print(f"❌ Failed to start {service_name}: {e}")
            return False
    
    def start_all_services(self):
        """Start all services in the correct order"""
        print("🚨 AgentAid with Fixed Agent Communication")
        print("=" * 50)
        
        # Clean up existing processes
        self.kill_existing_processes()
        
        # Start Claude service first
        if not self.start_service('claude_service', self.services['claude_service']):
            print("❌ Failed to start Claude service. Exiting.")
            return False
        
        # Start supply agents (addresses are already configured in env_vars)
        supply_agents = ['supply_agent_emergency', 'supply_agent_family']
        
        for agent_name in supply_agents:
            if self.start_service(agent_name, self.services[agent_name]):
                print(f"✅ {agent_name} started")
            else:
                print(f"⚠️  Failed to start {agent_name}, continuing...")
        
        # Start need agent (supply addresses already configured)
        if not self.start_service('need_agent', self.services['need_agent']):
            print("⚠️  Failed to start need agent, continuing...")
        
        # Start coordination agent last
        if not self.start_service('coordination_agent', self.services['coordination_agent']):
            print("⚠️  Failed to start coordination agent, continuing...")
        
        print("\n🎯 All services started!")
        print("\n📊 Service Status:")
        for process_info in self.processes:
            status = "Running" if process_info['process'].poll() is None else "Stopped"
            print(f"   {process_info['name']}: {status}")
        
        print("\n🏥 Dummy Suppliers Available:")
        print("   🚑 Emergency Medical & Fire Response Depot")
        print("      - 500 blankets")
        print("      - 10 ambulances")
        print("      - Burn medicines & medical supplies")
        print("      - Location: San Francisco")
        print("      - Delivery: Ambulance (1h lead time)")
        
        print("\n   👶 Family & Child Emergency Supplies")
        print("      - 10 emergency baby food cases")
        print("      - 20 diaper packs")
        print("      - 50 blankets")
        print("      - Baby formula, clothes, toys")
        print("      - Location: Oakland")
        print("      - Delivery: Van (1.5h lead time)")
        
        print("\n🌐 Access Points:")
        print("   Disaster Response UI: http://localhost:3000/disaster-response.html")
        print("   Claude Service API: http://localhost:3000/health")
        print("   Coordination Agent: Port 8002")
        print("   Need Agent: Port 8000")
        print("   Supply Agents: Ports 8001, 8003")
        
        print("\n🧪 Test Scenario:")
        print("   Try requesting: 'We need 100 blankets at the community center'")
        print("   The system will coordinate between both suppliers to fulfill the request!")
        
        return True
    
    def monitor_services(self):
        """Monitor running services with better error handling"""
        print("\n👀 Monitoring services... (Press Ctrl+C to stop)")
        
        try:
            while True:
                time.sleep(10)
                
                # Check if any process has died
                dead_processes = []
                for process_info in self.processes:
                    if process_info['process'].poll() is not None:
                        dead_processes.append(process_info['name'])
                
                if dead_processes:
                    print(f"⚠️  Services stopped: {', '.join(dead_processes)}")
                    print("   This is normal - agents may restart automatically")
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down services...")
            self.stop_all_services()
    
    def stop_all_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping all services...")
        
        for process_info in self.processes:
            try:
                process_info['process'].terminate()
                process_info['process'].wait(timeout=5)
                print(f"✅ {process_info['name']} stopped")
            except subprocess.TimeoutExpired:
                process_info['process'].kill()
                print(f"🔪 {process_info['name']} force killed")
            except Exception as e:
                print(f"⚠️  Error stopping {process_info['name']}: {e}")
        
        print("🏁 All services stopped")
    
    def run(self):
        """Main entry point"""
        try:
            if self.start_all_services():
                self.monitor_services()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        finally:
            self.stop_all_services()

def main():
    """Main function"""
    print("🚨 AgentAid Fixed Startup")
    print("Starting integrated AI coordination system with fixed agent communication...")
    
    # Check if we're in the right directory
    if not Path('agentaid-claude-service').exists():
        print("❌ Please run this script from the agent-aid root directory")
        sys.exit(1)
    
    # Start the orchestrator
    orchestrator = FixedAgentAidOrchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()
