#!/usr/bin/env python3
"""
Keep AgentAid agents running continuously
"""

import subprocess
import time
import os
import signal
import sys
from pathlib import Path

class AgentManager:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        
    def start_agent(self, name, command, cwd=None):
        """Start an agent and keep it running"""
        print(f"🚀 Starting {name}...")
        
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd or self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append({
                'name': name,
                'process': process,
                'command': command
            })
            
            print(f"✅ {name} started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return False
    
    def monitor_agents(self):
        """Monitor agents and restart if they die"""
        print("\n👀 Monitoring agents... (Press Ctrl+C to stop)")
        
        try:
            while True:
                time.sleep(5)
                
                # Check if any process has died
                for process_info in self.processes:
                    if process_info['process'].poll() is not None:
                        print(f"⚠️  {process_info['name']} stopped, restarting...")
                        
                        # Restart the agent
                        new_process = subprocess.Popen(
                            process_info['command'],
                            cwd=self.base_dir / "fetchai-agents",
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            bufsize=1,
                            universal_newlines=True
                        )
                        
                        process_info['process'] = new_process
                        print(f"✅ {process_info['name']} restarted (PID: {new_process.pid})")
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down agents...")
            self.stop_all_agents()
    
    def stop_all_agents(self):
        """Stop all running agents"""
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
    
    def run(self):
        """Main entry point"""
        print("🚨 AgentAid - Keep Agents Running")
        print("=" * 50)
        
        # Start supply agent first
        if not self.start_agent(
            "Supply Agent",
            ["python3", "supply_agent_fixed.py"],
            self.base_dir / "fetchai-agents"
        ):
            print("❌ Failed to start supply agent")
            return
        
        # Wait a moment
        time.sleep(2)
        
        # Start need agent
        if not self.start_agent(
            "Need Agent", 
            ["python3", "need_agent_fixed.py"],
            self.base_dir / "fetchai-agents"
        ):
            print("❌ Failed to start need agent")
            return
        
        print("\n🎯 All agents started and will stay running!")
        print("📊 Service URLs:")
        print("   Need Agent:   http://localhost:8000")
        print("   Supply Agent: http://localhost:8001")
        print("   Claude UI:    http://localhost:3000/chat.html")
        
        # Monitor and restart if needed
        self.monitor_agents()

def main():
    """Main function"""
    manager = AgentManager()
    
    try:
        manager.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    finally:
        manager.stop_all_agents()

if __name__ == "__main__":
    main()
