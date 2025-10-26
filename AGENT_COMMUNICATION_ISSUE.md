# Agent Communication Issue

## Problem
The agents cannot communicate with each other because the uAgent framework is trying to resolve agent addresses using the **AlmanacApiResolver** (remote service) instead of using local endpoints.

## Error
```
ERROR: [resolver]: Error in AlmanacApiResolver when resolving agent1qvp9jjj2rjtnj5nhnrnvmnm856l8t6gs7uyjw9ucpunepz9fmvpr5r4q8q3
ERROR: [coordination_agent_1]: Unable to resolve destination endpoint for agent
```

## Root Cause
- Agents are configured with local endpoints (e.g., `http://127.0.0.1:8001/submit`)
- But when sending messages, the uAgent framework tries to resolve addresses via Almanac API
- Since these agents aren't registered in the remote Almanac, resolution fails
- Messages never get delivered

## What Works
✅ Coordination agent discovers agents from environment variables
✅ Coordination agent finds pending requests
✅ Coordination agent attempts to send messages
✅ All agents have endpoints configured
✅ All agents include the AidProtocol

## What Doesn't Work
❌ Message delivery between agents
❌ Agent address resolution
❌ Local agent-to-agent communication

## Solutions

### Option 1: Register agents in Almanac (Complex)
- Register all agents in the Fetch.ai Almanac
- Requires internet connection
- Requires Almanac API keys
- Not ideal for local development

### Option 2: Use local agent bureau (Recommended)
- Use uAgents Bureau for local agent management
- Agents can discover each other locally
- No remote dependencies

### Option 3: Direct HTTP communication (Simplest)
- Bypass uAgent messaging
- Use direct HTTP calls to agent endpoints
- Agents already have HTTP endpoints configured

### Option 4: Simplified architecture
- Remove agent-to-agent communication
- Have all agents poll Claude service directly
- Claude service acts as message broker

## Current Status
The system is architecturally sound but hits a framework limitation with local agent resolution.
The UI shows "Request is being processed..." indefinitely because agents never complete the request flow.
