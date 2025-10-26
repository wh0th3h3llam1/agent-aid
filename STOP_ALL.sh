#!/bin/bash
# Stop all AgentAid services

echo "🛑 Stopping AgentAid System"
echo "======================================"
echo ""

# Check if tmux session exists
if tmux has-session -t agentaid 2>/dev/null; then
    echo "Stopping tmux session..."
    tmux kill-session -t agentaid
    echo "✅ Tmux session stopped"
else
    echo "Stopping background processes..."
    
    # Kill Node.js (Claude Service)
    pkill -f "node server.js" && echo "✅ Claude Service stopped"
    
    # Kill Python agents
    pkill -f "need_agent_fixed.py" && echo "✅ Need Agent stopped"
    pkill -f "supply_agent_fixed.py" && echo "✅ Supply Agent stopped"
fi

# Also kill any other related processes
pkill -f "coordinator" 2>/dev/null

echo ""
echo "======================================"
echo "✅ All services stopped!"
echo "======================================"
echo ""
