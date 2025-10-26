#!/usr/bin/env python3
"""
Fresh start with 2 supply agents
"""
import os
import sys
import time
import subprocess
import signal
from pathlib import Path

class FreshAgentSystem:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        
        self.services = {
            'claude_service': {
                'path': self.base_dir / 'agentaid-claude-service',
                'command': ['node', 'server.js'],
                'port': 3000,
            },
            'medical_emergency_depot': {
                'path': self.base_dir / 'agentaid-marketplace',
                'command': ['python', 'agents/supply_agent_polling.py'],
                'env_vars': {
                    'SUPPLIER_NAME': 'medical_emergency_depot',
                    'SUPPLIER_PORT': '8001',
                    'SUPPLIER_LAT': '37.7749',  # San Francisco
                    'SUPPLIER_LON': '-122.4194',
                    'SUPPLIER_LABEL': 'Medical Emergency Depot',
                    'SUPPLIER_LEAD_H': '1.0',
                    'SUPPLIER_RADIUS_KM': '200.0',
                    'SUPPLIER_DELIVERY_MODE': 'ambulance',
                    'CLAUDE_SERVICE_URL': 'http://localhost:3000'
                }
            },
            'community_relief_center': {
                'path': self.base_dir / 'agentaid-marketplace',
                'command': ['python', 'agents/supply_agent_polling.py'],
                'env_vars': {
                    'SUPPLIER_NAME': 'community_relief_center',
                    'SUPPLIER_PORT': '8002',
                    'SUPPLIER_LAT': '37.8044',  # Oakland
                    'SUPPLIER_LON': '-122.2712',
                    'SUPPLIER_LABEL': 'Community Relief Center',
                    'SUPPLIER_LEAD_H': '1.5',
                    'SUPPLIER_RADIUS_KM': '150.0',
                    'SUPPLIER_DELIVERY_MODE': 'truck',
                    'CLAUDE_SERVICE_URL': 'http://localhost:3000'
                }
            },
            'need_agent': {
                'path': self.base_dir / 'agentaid-marketplace',
                'command': ['python', 'agents/need_agent_polling.py'],
                'env_vars': {
                    'NEED_AGENT_NAME': 'need_agent_coordinator',
                    'NEED_AGENT_PORT': '8000',
                    'CLAUDE_SERVICE_URL': 'http://localhost:3000'
                }
            }
        }
    
    def setup_suppliers(self):
        """Setup suppliers in database"""
        print("🔧 Setting up suppliers...")
        try:
            result = subprocess.run(
                [sys.executable, str(self.base_dir / 'setup_fresh_suppliers.py')],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print("⚠️  Suppliers may already exist")
                return True
        except Exception as e:
            print(f"⚠️  Setup error: {e}")
            return True
    
    def kill_existing(self):
        """Kill existing processes"""
        print("🧹 Cleaning up...")
        for port in [3000, 8001, 8002]:
            try:
                result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
                if result.stdout.strip():
                    for pid in result.stdout.strip().split('\n'):
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                        except:
                            pass
            except:
                pass
        time.sleep(2)
    
    def start_service(self, name, config):
        """Start a service"""
        print(f"🚀 Starting {name}...")
        
        env = os.environ.copy()
        if 'env_vars' in config:
            env.update(config['env_vars'])
        
        os.chdir(config['path'])
        
        try:
            process = subprocess.Popen(
                config['command'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(2)
            
            if process.poll() is None:
                print(f"   ✅ {name} started (PID: {process.pid})")
                self.processes.append({'name': name, 'process': process})
                return True
            else:
                print(f"   ❌ {name} failed")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def start_all(self):
        """Start all services"""
        print("=" * 60)
        print("🚨 AgentAid - Fresh Start")
        print("=" * 60)
        
        self.kill_existing()
        self.setup_suppliers()
        
        print("\n📦 Starting Services...")
        
        # Start Claude service
        if not self.start_service('claude_service', self.services['claude_service']):
            return False
        
        time.sleep(3)
        
        # Start supply agents
        self.start_service('medical_emergency_depot', self.services['medical_emergency_depot'])
        time.sleep(1)
        self.start_service('community_relief_center', self.services['community_relief_center'])
        time.sleep(1)
        
        # Start need agent (coordinator)
        self.start_service('need_agent', self.services['need_agent'])
        
        print("\n" + "=" * 60)
        print("✅ ALL SYSTEMS READY!")
        print("=" * 60)
        
        print("\n📊 Active Suppliers:")
        print("   🏥 Medical Emergency Depot (San Francisco)")
        print("      - 300 blankets, 100 first aid kits")
        print("      - 500 water bottles, 150 flashlights")
        print("      - Radius: 200 km, ETA: 1 hour")
        
        print("\n   🏪 Community Relief Center (Oakland)")
        print("      - 150 blankets, 200 food packages")
        print("      - 300 water bottles, 80 clothing sets")
        print("      - Radius: 150 km, ETA: 1.5 hours")
        
        print("\n🌐 OPEN THE UI:")
        print("   👉 http://localhost:3000/disaster-response.html")
        
        print("\n🤖 Need Agent (Coordinator):")
        print("   - Collects quotes from all suppliers")
        print("   - Evaluates based on cost, speed, coverage")
        print("   - Negotiates and selects best supplier")
        print("   - Confirms allocation")
        
        print("\n💡 Test Request:")
        print("   'We need 50 blankets in San Francisco. Contact: 555-1234'")
        
        print("\n⏱️  How it works:")
        print("   1. Supply agents poll every 5 seconds → send quotes")
        print("   2. Need agent waits 10 seconds → collects all quotes")
        print("   3. Need agent negotiates → selects best supplier")
        print("   4. UI shows quotes + selected supplier within 15 seconds!")
        
        print("\n👀 Monitoring... (Press Ctrl+C to stop)")
        return True
    
    def monitor(self):
        """Monitor services"""
        try:
            while True:
                time.sleep(10)
                for p in self.processes:
                    if p['process'].poll() is not None:
                        print(f"\n⚠️  {p['name']} stopped!")
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
            for p in self.processes:
                try:
                    p['process'].terminate()
                    p['process'].wait(timeout=5)
                except:
                    try:
                        p['process'].kill()
                    except:
                        pass
            print("✅ Shutdown complete")

def main():
    system = FreshAgentSystem()
    if system.start_all():
        system.monitor()
    else:
        print("\n❌ Failed to start")
        sys.exit(1)

if __name__ == "__main__":
    main()
