#!/usr/bin/env python3
"""
Start AgentAid with polling-based agents (message broker pattern)
"""
import os
import sys
import time
import subprocess
import signal
from pathlib import Path

class PollingAgentOrchestrator:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        
        # Setup inventory
        self.setup_inventory()
        
        self.services = {
            'claude_service': {
                'path': self.base_dir / 'agentaid-claude-service',
                'command': ['node', 'server.js'],
                'port': 3000,
            },
            'supply_agent_emergency': {
                'path': self.base_dir / 'agentaid-marketplace',
                'command': ['python', 'agents/supply_agent_polling.py'],
                'env_vars': {
                    'SUPPLIER_NAME': 'emergency_medical_fire',
                    'SUPPLIER_PORT': '8001',
                    'SUPPLIER_LAT': '37.7749',
                    'SUPPLIER_LON': '-122.4194',
                    'SUPPLIER_LABEL': 'Emergency Medical & Fire Response Depot',
                    'SUPPLIER_LEAD_H': '1.0',
                    'SUPPLIER_RADIUS_KM': '150.0',
                    'SUPPLIER_DELIVERY_MODE': 'ambulance',
                    'CLAUDE_SERVICE_URL': 'http://localhost:3000'
                }
            },
            'supply_agent_family': {
                'path': self.base_dir / 'agentaid-marketplace',
                'command': ['python', 'agents/supply_agent_polling.py'],
                'env_vars': {
                    'SUPPLIER_NAME': 'family_child_emergency',
                    'SUPPLIER_PORT': '8003',
                    'SUPPLIER_LAT': '37.8044',
                    'SUPPLIER_LON': '-122.2712',
                    'SUPPLIER_LABEL': 'Family & Child Emergency Supplies Depot',
                    'SUPPLIER_LEAD_H': '1.5',
                    'SUPPLIER_RADIUS_KM': '120.0',
                    'SUPPLIER_DELIVERY_MODE': 'van',
                    'CLAUDE_SERVICE_URL': 'http://localhost:3000'
                }
            }
        }
    
    def setup_inventory(self):
        """Setup inventory in database"""
        print("🏥 Setting up inventory...")
        try:
            result = subprocess.run(
                [sys.executable, str(self.base_dir / 'populate_inventory.py')],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            if result.returncode == 0:
                print("✅ Inventory setup complete")
            else:
                print("⚠️  Inventory setup had issues (may already exist)")
        except Exception as e:
            print(f"⚠️  Inventory setup error: {e}")
    
    def kill_existing_processes(self):
        """Kill any existing processes on our ports"""
        print("🧹 Cleaning up existing processes...")
        ports = [3000, 8001, 8003]
        
        for port in ports:
            try:
                result = subprocess.run(
                    ['lsof', '-ti', f':{port}'],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            print(f"   🔪 Killed process {pid} on port {port}")
                        except:
                            pass
            except:
                pass
        
        time.sleep(2)
    
    def start_service(self, service_name, service_config):
        """Start a single service"""
        print(f"\n🚀 Starting {service_name}...")
        
        env = os.environ.copy()
        if 'env_vars' in service_config:
            env.update(service_config['env_vars'])
        
        os.chdir(service_config['path'])
        
        try:
            process = subprocess.Popen(
                service_config['command'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(2)
            
            if process.poll() is None:
                print(f"✅ {service_name} started (PID: {process.pid})")
                self.processes.append({
                    'name': service_name,
                    'process': process,
                    'config': service_config
                })
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {service_name} failed to start")
                if stderr:
                    print(f"   Error: {stderr[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start {service_name}: {e}")
            return False
    
    def start_all_services(self):
        """Start all services"""
        print("🚨 AgentAid with Polling Agents (Message Broker Pattern)")
        print("=" * 60)
        
        self.kill_existing_processes()
        
        # Start Claude service first
        if not self.start_service('claude_service', self.services['claude_service']):
            print("❌ Failed to start Claude service. Exiting.")
            return False
        
        time.sleep(3)
        
        # Start supply agents
        for agent_name in ['supply_agent_emergency', 'supply_agent_family']:
            self.start_service(agent_name, self.services[agent_name])
            time.sleep(2)
        
        print("\n🎯 All services started!")
        print("\n📊 Service Status:")
        for process_info in self.processes:
            status = "Running" if process_info['process'].poll() is None else "Stopped"
            print(f"   {process_info['name']}: {status}")
        
        print("\n🏥 Suppliers:")
        print("   🚑 Emergency Medical & Fire Response Depot")
        print("      - 500 blankets, 10 ambulances, burn medicine")
        print("      - Polling every 5 seconds")
        
        print("\n   👶 Family & Child Emergency Supplies")
        print("      - 50 blankets, baby food, diapers")
        print("      - Polling every 5 seconds")
        
        print("\n🌐 Access Points:")
        print("   Disaster Response UI: http://localhost:3000/disaster-response.html")
        print("   Claude Service API: http://localhost:3000/health")
        
        print("\n💡 How it works:")
        print("   1. Submit request via UI")
        print("   2. Claude extracts and stores request")
        print("   3. Supply agents poll for pending requests")
        print("   4. Agents send quotes back to Claude service")
        print("   5. Best quote is selected automatically")
        
        print("\n👀 Monitoring services... (Press Ctrl+C to stop)")
        return True
    
    def monitor_services(self):
        """Monitor running services"""
        try:
            while True:
                time.sleep(10)
                
                # Check if any process died
                for process_info in self.processes:
                    if process_info['process'].poll() is not None:
                        print(f"\n⚠️  {process_info['name']} stopped unexpectedly")
                        
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down services...")
            self.stop_all_services()
    
    def stop_all_services(self):
        """Stop all running services"""
        for process_info in self.processes:
            try:
                process_info['process'].terminate()
                process_info['process'].wait(timeout=5)
                print(f"   ✅ Stopped {process_info['name']}")
            except:
                try:
                    process_info['process'].kill()
                except:
                    pass
        
        print("\n👋 All services stopped")

def main():
    orchestrator = PollingAgentOrchestrator()
    
    if orchestrator.start_all_services():
        orchestrator.monitor_services()
    else:
        print("\n❌ Failed to start services")
        sys.exit(1)

if __name__ == "__main__":
    main()
