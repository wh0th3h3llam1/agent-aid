#!/bin/bash
# Test script for direct agent communication

echo "🧪 Testing Direct Agent Communication"
echo "======================================"
echo ""

# Test 1: Basic request
echo "Test 1: Basic blanket request"
echo "------------------------------"
curl -X POST http://localhost:8000/request \
  -H "Content-Type: application/json" \
  -d '{"message": "Need 50 blankets in Oakland"}' \
  -s | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))"

echo ""
echo "⏱️  Waiting 12 seconds for quote evaluation..."
sleep 12
echo ""

# Test 2: Critical priority
echo "Test 2: Critical priority request"
echo "----------------------------------"
curl -X POST http://localhost:8000/request \
  -H "Content-Type: application/json" \
  -d '{"message": "Emergency! Need 100 medical supplies in San Francisco. Critical priority. 200 people affected."}' \
  -s | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))"

echo ""
echo "⏱️  Waiting 12 seconds for quote evaluation..."
sleep 12
echo ""

# Test 3: Multiple items
echo "Test 3: Multiple items request"
echo "-------------------------------"
curl -X POST http://localhost:8000/request \
  -H "Content-Type: application/json" \
  -d '{"message": "Need 200 blankets and 500 water bottles in Berkeley. High priority."}' \
  -s | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))"

echo ""
echo "⏱️  Waiting 12 seconds for quote evaluation..."
sleep 12
echo ""

# Check supply agent inventory
echo "Test 4: Check supply agent inventory"
echo "-------------------------------------"
curl -s http://localhost:8001/inventory | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Supplier: {data['supplier']}\"); print(f\"Total Units: {data['total_units']}\"); print('\\nInventory:'); [print(f'  - {k}: {v[\"available\"]} {v[\"unit\"]}') for k,v in data['inventory'].items()]"

echo ""
echo "======================================"
echo "✅ Tests complete!"
echo "======================================"
echo ""
echo "📝 Check agent logs to see the message exchange:"
echo "   - Need Agent: Terminal where direct_need_agent.py is running"
echo "   - Supply Agent: Terminal where direct_supply_agent.py is running"
echo ""
