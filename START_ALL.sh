#!/bin/bash
# Start all components of AgentAid system

echo "🚀 Starting AgentAid System"
echo "======================================"
echo ""

# Check if tmux is available
if ! command -v tmux &> /dev/null; then
    echo "⚠️  tmux not found. Installing is recommended for better process management."
    echo "   Install with: brew install tmux"
    echo ""
    echo "Starting services in background instead..."
    
    # Create logs directory
    mkdir -p logs
    
    # Start Claude Service
    echo "1️⃣  Starting Claude Service..."
    cd agentaid-claude-service
    nohup node server.js > ../logs/claude-service.log 2>&1 &
    CLAUDE_PID=$!
    echo "   PID: $CLAUDE_PID"
    cd ..
    
    # Wait for Claude service to start
    sleep 3
    
    # Start Need Agent
    echo "2️⃣  Starting Need Agent..."
    cd fetchai-agents
    nohup python3 need_agent_fixed.py > ../logs/need-agent.log 2>&1 &
    NEED_PID=$!
    echo "   PID: $NEED_PID"
    cd ..
    
    # Wait a moment
    sleep 2
    
    # Start Supply Agent
    echo "3️⃣  Starting Supply Agent..."
    cd fetchai-agents
    nohup python3 supply_agent_fixed.py > ../logs/supply-agent.log 2>&1 &
    SUPPLY_PID=$!
    echo "   PID: $SUPPLY_PID"
    cd ..
    
    echo ""
    echo "======================================"
    echo "✅ All services started!"
    echo "======================================"
    echo ""
    echo "📊 Service URLs:"
    echo "   Chat UI:      http://localhost:3000/chat.html"
    echo "   Claude API:   http://localhost:3000"
    echo "   Need Agent:   http://localhost:8000/status"
    echo "   Supply Agent: http://localhost:8001/status"
    echo ""
    echo "📝 Logs:"
    echo "   Claude:  tail -f logs/claude-service.log"
    echo "   Need:    tail -f logs/need-agent.log"
    echo "   Supply:  tail -f logs/supply-agent.log"
    echo ""
    echo "🛑 To stop all services:"
    echo "   ./STOP_ALL.sh"
    echo ""
    
else
    # Use tmux for better management
    echo "Using tmux for process management..."
    
    # Create new tmux session
    SESSION="agentaid"
    
    # Kill existing session if it exists
    tmux kill-session -t $SESSION 2>/dev/null
    
    # Create new session with Claude Service
    echo "1️⃣  Starting Claude Service..."
    tmux new-session -d -s $SESSION -n "claude" "cd agentaid-claude-service && node server.js"
    
    # Wait for Claude service
    sleep 3
    
    # Create window for Need Agent
    echo "2️⃣  Starting Need Agent..."
    tmux new-window -t $SESSION -n "need" "cd fetchai-agents && python3 need_agent_fixed.py"
    
    # Wait a moment
    sleep 2
    
    # Create window for Supply Agent
    echo "3️⃣  Starting Supply Agent..."
    tmux new-window -t $SESSION -n "supply" "cd fetchai-agents && python3 supply_agent_fixed.py"
    
    echo ""
    echo "======================================"
    echo "✅ All services started in tmux!"
    echo "======================================"
    echo ""
    echo "📊 Service URLs:"
    echo "   Chat UI:      http://localhost:3000/chat.html"
    echo "   Claude API:   http://localhost:3000"
    echo "   Need Agent:   http://localhost:8000/status"
    echo "   Supply Agent: http://localhost:8001/status"
    echo ""
    echo "🔍 To view services:"
    echo "   tmux attach -t $SESSION"
    echo ""
    echo "   Switch windows: Ctrl+B then 0/1/2"
    echo "   Window 0: Claude Service"
    echo "   Window 1: Need Agent"
    echo "   Window 2: Supply Agent"
    echo ""
    echo "🛑 To stop all services:"
    echo "   ./STOP_ALL.sh"
    echo ""
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo "🎯 System is ready! Open http://localhost:3000/chat.html to start"
echo ""
