@echo off
REM Quick deployment script for Agentverse (Windows)

echo ==========================================
echo AgentAid Agentverse Deployment
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 not found. Please install Python 3.8+
    exit /b 1
)

echo.
echo Installing dependencies...
pip install fastapi uvicorn uagents-core httpx

echo.
echo ==========================================
echo Step 1: Create Public Tunnels
echo ==========================================
echo.
echo You need cloudflared installed. Download from:
echo https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
echo.
echo Open TWO new command prompt windows and run:
echo.
echo Window 1 (Need Agent):
echo   cloudflared tunnel --url http://localhost:8000
echo.
echo Window 2 (Supply Agent):
echo   cloudflared tunnel --url http://localhost:8001
echo.
pause

echo.
echo ==========================================
echo Step 2: Set Environment Variables
echo ==========================================
echo.
set /p NEED_URL="Enter Need Agent tunnel URL (e.g., https://abc123.trycloudflare.com): "
set /p SUPPLY_URL="Enter Supply Agent tunnel URL (e.g., https://def456.trycloudflare.com): "

echo.
echo Environment variables set
echo Need Agent URL: %NEED_URL%
echo Supply Agent URL: %SUPPLY_URL%

echo.
echo ==========================================
echo Step 3: Start Agents
echo ==========================================
echo.
echo Open TWO more command prompt windows and run:
echo.
echo Window 3 (Need Agent):
echo   cd agentaid-marketplace\agents
echo   set AGENT_EXTERNAL_ENDPOINT=%NEED_URL%
echo   set AGENT_SEED_PHRASE=need_agent_berkeley_1_demo_seed
echo   python need_agent_chat_adapter.py
echo.
echo Window 4 (Supply Agent):
echo   cd agentaid-marketplace\agents
echo   set AGENT_EXTERNAL_ENDPOINT=%SUPPLY_URL%
echo   set AGENT_SEED_PHRASE=supply_sf_store_1_demo_seed
echo   set SUPPLIER_LABEL=SF Depot
echo   python supply_agent_chat_adapter.py
echo.
pause

echo.
echo ==========================================
echo Step 4: Test Endpoints
echo ==========================================
echo.
echo Testing Need Agent...
curl -s "%NEED_URL%/status"

echo.
echo Testing Supply Agent...
curl -s "%SUPPLY_URL%/status"

echo.
echo ==========================================
echo Step 5: Register on Agentverse
echo ==========================================
echo.
echo Run the registration scripts:
echo.
echo For Need Agent:
echo   cd agentaid-marketplace
echo   set AGENT_EXTERNAL_ENDPOINT=%NEED_URL%
echo   python register_need_agent.py
echo.
echo For Supply Agent:
echo   set AGENT_EXTERNAL_ENDPOINT=%SUPPLY_URL%
echo   python register_supply_agent.py
echo.
echo Then follow the instructions to complete registration on Agentverse
echo.
echo ==========================================
echo Deployment Guide Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Go to https://agentverse.ai/
echo 2. Click 'Launch an Agent'
echo 3. Select 'Chat Protocol'
echo 4. Use the URLs and information from the registration scripts
echo 5. Test your agents in ASI:One chat
echo.
echo For detailed instructions, see: AGENTVERSE_DEPLOYMENT.md
echo ==========================================
pause
