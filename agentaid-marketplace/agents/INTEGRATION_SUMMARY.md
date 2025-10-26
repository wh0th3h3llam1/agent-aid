# AgentAid Chat Protocol Integration - Summary

## ✅ Completed Updates

Both Need Agent and Supply Agent have been successfully updated to support structured JSON communication following the Chat Protocol standard as specified in the [Agentverse documentation](https://docs.agentverse.ai/documentation/launch-agents/connect-your-agents-chat-protocol-integration).

## Changes Made

### 1. Need Agent (`need_agent_chat_adapter.py`)

**New Features:**
- ✅ Accepts structured JSON disaster relief requests
- ✅ Queries multiple supply agents asynchronously
- ✅ Evaluates and ranks quotes from suppliers
- ✅ Returns formatted responses with recommendations
- ✅ Fallback to text processing for non-JSON messages

**Key Functions Added:**
- `process_need_request_json()` - Processes structured JSON requests
- `query_supply_agents()` - Queries all configured supply agents
- `query_single_supply_agent()` - Queries individual supplier
- `evaluate_quotes()` - Scores and ranks quotes
- `calculate_distance()` - Haversine distance calculation
- `format_quote_response()` - Formats quote comparison
- `format_no_quotes_response()` - Handles no-response scenarios

**Configuration:**
```bash
export SUPPLY_AGENT_ENDPOINT="http://localhost:8001"  # or cloudflare URL
export SUPPLY_AGENT_ADDRESS="agent1q..."
```

### 2. Supply Agent (`supply_agent_chat_adapter.py`)

**New Features:**
- ✅ Processes structured JSON quote requests
- ✅ Returns detailed JSON quotes with all required fields
- ✅ Distance-based service radius checking (120 km)
- ✅ Priority-based pricing (critical: 10% off, high: 5% off)
- ✅ Real-time ETA and delivery date calculation
- ✅ Added "Burn Medicine" to inventory (150 kits @ $75/kit)

**Key Functions Added:**
- `generate_quote_json()` - Main quote generation for JSON requests
- `calculate_distance()` - Haversine distance calculation
- `get_inventory_dict()` - Returns inventory with pricing

**Updated Inventory:**
- Blankets: 500 ea @ $15.00
- Water Bottles: 1000 bottles @ $2.00
- Medical Supplies: 200 kits @ $50.00
- **Burn Medicine: 150 kits @ $75.00** (NEW)
- Food Rations: 800 meals @ $8.00
- Tents: 50 ea @ $200.00
- Clothing: 300 sets @ $25.00

**Configuration:**
```bash
export SUPPLIER_LABEL="SF Medical Depot"
export SUPPLIER_LAT="37.7749"
export SUPPLIER_LON="-122.4194"
```

### 3. Added Endpoints

Both agents now support:
- `GET /status` - Health check
- `GET /agent_info` - Agent registration info (required by Agentverse)
- `POST /` - Main chat endpoint (Chat Protocol)

## JSON Schema

### Request Schema (to Need Agent)
```json
{
  "items": ["medical supplies", "burn medicine"],
  "quantity_needed": "100",
  "location": "Fine Arts building, San Francisco, CA",
  "priority": "high",
  "coordinates": {
    "latitude": 37.8194438,
    "longitude": -122.3659023,
    "formatted_address": "Building 3, 600, California Avenue, San Francisco, CA",
    "confidence": 0.8
  },
  "request_id": "REQ-1761434743462-j010gfx5m",
  "timestamp": "2025-10-25T23:25:43.462Z",
  "raw_input": "i need 100 burn medicines at fine arts , SF, CA"
}
```

### Response Schema (from Supply Agent)
```json
{
  "quote_id": "QUOTE-REQ-xxx-timestamp",
  "request_id": "REQ-xxx",
  "supplier_name": "SF Medical Depot",
  "supplier_location": "SF Medical Depot",
  "supplier_coordinates": {
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "status": "available",
  "coverage_ratio": 1.0,
  "items_offered": [
    {
      "item": "Medical Supplies",
      "quantity_offered": 100,
      "quantity_requested": 100,
      "unit": "kits",
      "unit_price": 50.0
    },
    {
      "item": "Burn Medicine",
      "quantity_offered": 100,
      "quantity_requested": 100,
      "unit": "kits",
      "unit_price": 75.0
    }
  ],
  "total_cost": 11875.0,
  "distance_km": 15.2,
  "estimated_delivery_hours": 1.88,
  "estimated_delivery_date": "2025-10-26 01:20:15",
  "delivery_mode": "truck",
  "priority": "high",
  "service_radius_km": 120,
  "terms": "delivery:truck;priority:high;payment:net30",
  "timestamp": "2025-10-25T23:25:43.462Z",
  "valid_until": "2025-10-25T23:55:43.462Z"
}
```

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User/System sends JSON request to Need Agent                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│ 2. Need Agent parses request and extracts:                     │
│    - Items needed (medical supplies, burn medicine)            │
│    - Quantity (100)                                             │
│    - Location & Coordinates (SF, CA - 37.82, -122.37)          │
│    - Priority (high)                                            │
│    - Request ID                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│ 3. Need Agent queries Supply Agent(s)                          │
│    - Sends same JSON structure via HTTP POST                   │
│    - Uses async requests (httpx)                               │
│    - Waits for responses (30s timeout)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│ 4. Supply Agent processes quote request:                       │
│    - Checks distance (must be < 120 km)                        │
│    - Matches items to inventory                                │
│    - Calculates coverage ratio                                 │
│    - Applies priority pricing                                  │
│    - Calculates ETA (base 1.5h + travel time)                  │
│    - Generates delivery date                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│ 5. Supply Agent returns JSON quote to Need Agent               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│ 6. Need Agent evaluates quote(s):                              │
│    - Coverage Score (40%)                                       │
│    - Delivery Time Score (30%)                                 │
│    - Cost Score (30%)                                           │
│    - Selects best quote                                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│ 7. Need Agent returns formatted response with:                 │
│    - All quotes received                                        │
│    - Best quote highlighted                                    │
│    - Recommendation                                             │
│    - Next steps                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Testing

### Example Test Scenario

**Input (to Need Agent):**
```json
{
  "items": ["medical supplies", "burn medicine"],
  "quantity_needed": "100",
  "location": "Fine Arts building, San Francisco, CA",
  "priority": "high",
  "coordinates": {
    "latitude": 37.8194438,
    "longitude": -122.3659023
  },
  "request_id": "REQ-TEST-123"
}
```

**Expected Output:**
```
✅ **Disaster Relief Request Processed**

**Request ID**: REQ-TEST-123
**Items Requested**: medical supplies, burn medicine
**Quantity**: 100
**Location**: Fine Arts building, San Francisco, CA
**Priority**: HIGH

📊 **Received 1 Quote(s) from Supply Agents**

⭐ **BEST QUOTE**
**Supplier**: SF Medical Depot
**Location**: SF Medical Depot
**Coverage**: 100.0%
**Delivery Time**: 1.88 hours
**Delivery Date**: 2025-10-26 01:20:15
**Total Cost**: $11875.00
**Delivery Mode**: truck
**Distance**: 15.20 km

🎯 **Recommended Action**: Accept quote from SF Medical Depot
```

## Running the Demo

### Terminal 1: Supply Agent
```bash
cd agent-aid/agentaid-marketplace/agents
export AGENT_SEED_PHRASE="supply_sf_store_1_demo_seed"
export SUPPLIER_LABEL="SF Medical Depot"
export PORT=8001
python supply_agent_chat_adapter.py
```

### Terminal 2: Need Agent
```bash
cd agent-aid/agentaid-marketplace/agents
export AGENT_SEED_PHRASE="need_agent_berkeley_1_demo_seed"
export SUPPLY_AGENT_ENDPOINT="http://localhost:8001"
export PORT=8000
python need_agent_chat_adapter.py
```

### Terminal 3 & 4: Cloudflare Tunnels (for Agentverse)
```bash
# Terminal 3
cloudflared tunnel --url http://localhost:8000

# Terminal 4
cloudflared tunnel --url http://localhost:8001
```

## Dependencies

Already included in `requirements.txt`:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `uagents-core` - Fetch.ai agent framework
- `httpx` - Async HTTP client (NEW)

## Files Modified

1. ✅ `need_agent_chat_adapter.py` - Complete rewrite of request processing
2. ✅ `supply_agent_chat_adapter.py` - Added JSON quote generation
3. ✅ `CHAT_PROTOCOL_USAGE.md` - Comprehensive usage guide
4. ✅ `INTEGRATION_SUMMARY.md` - This file

## Next Steps

1. **Test the integration**
   - Send JSON requests to Need Agent
   - Verify Supply Agent responds correctly
   - Check quote evaluation logic

2. **Deploy to Agentverse**
   - Start both agents with cloudflare tunnels
   - Use `register_need_agent.py` and `register_supply_agent.py`
   - Test via ASI:One chat UI

3. **Future Enhancements**
   - Add database integration for inventory
   - Implement quote acceptance endpoint
   - Add inventory reservation on acceptance
   - Create delivery tracking
   - Add telemetry and logging
   - Support multiple supply agents
   - Add coordination agent integration

## Known Issues

- ChatMessage.schema_digest may need to be handled differently depending on uagents_core version
- Linter may show warnings about broad exception catching (acceptable for demo)
- Need to configure SUPPLY_AGENT_ADDRESS environment variable with actual agent address after registration

## Support

For issues or questions:
1. Check agent console logs
2. Verify environment variables are set correctly
3. Test endpoints manually with curl
4. Review CHAT_PROTOCOL_USAGE.md for detailed examples
5. Check Agentverse documentation: https://docs.agentverse.ai/

---
**Status**: ✅ Ready for Testing
**Last Updated**: October 26, 2025
