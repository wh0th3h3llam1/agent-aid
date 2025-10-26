# Chat Protocol Usage Guide for AgentAid

This guide explains how to use the updated Need Agent and Supply Agent with structured JSON communication.

## Overview

The agents now support structured JSON communication for disaster relief coordination:

1. **Need Agent** receives disaster relief requests in JSON format
2. **Need Agent** queries Supply Agents with the request
3. **Supply Agents** respond with detailed quotes including location, delivery date, cost, etc.
4. **Need Agent** evaluates quotes and recommends the best supplier

## Architecture

```
User/System → Need Agent (JSON Request) → Supply Agent(s) → Need Agent (Quotes) → User/System
```

## Need Agent

### Endpoint
- POST `/` - Receives disaster relief requests

### Input Schema

Send a JSON request in this format:

```json
{
  "items": [
    "medical supplies",
    "burn medicine"
  ],
  "quantity_needed": "100",
  "location": "Fine Arts building, San Francisco, CA",
  "priority": "high",
  "contact": null,
  "additional_notes": "Specifically requesting burn medicines",
  "victim_count": null,
  "coordinates": {
    "latitude": 37.8194438,
    "longitude": -122.3659023,
    "formatted_address": "Building 3, 600, California Avenue, San Francisco, California, 94130, United States of America",
    "confidence": 0.8
  },
  "timestamp": "2025-10-25T23:25:43.462Z",
  "raw_input": "i need 100 burn medicines at fine arts , SF, CA",
  "request_id": "REQ-1761434743462-j010gfx5m"
}
```

### Fields

- **items** (array): List of items needed (e.g., ["medical supplies", "burn medicine"])
- **quantity_needed** (string): Total quantity needed
- **location** (string): Human-readable location
- **priority** (string): "critical", "high", "medium", or "low"
- **coordinates** (object):
  - **latitude** (float): Latitude coordinate
  - **longitude** (float): Longitude coordinate
  - **formatted_address** (string): Full formatted address
  - **confidence** (float): Geocoding confidence score
- **request_id** (string): Unique request identifier
- **contact** (string, optional): Contact information
- **victim_count** (number, optional): Number of people affected
- **additional_notes** (string, optional): Additional details
- **timestamp** (string): ISO 8601 timestamp
- **raw_input** (string): Original user input

### Response

The Need Agent will:
1. Parse the JSON request
2. Query all configured supply agents
3. Collect quotes from suppliers
4. Evaluate and rank quotes
5. Return a formatted response with all quotes and recommendation

Example response:
```
✅ **Disaster Relief Request Processed**

**Request ID**: REQ-1761434743462-j010gfx5m
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
**Total Cost**: $7125.00
**Delivery Mode**: truck
**Distance**: 15.20 km

🎯 **Recommended Action**: Accept quote from SF Medical Depot
```

## Supply Agent

### Endpoint
- POST `/` - Receives quote requests from Need Agent

### Input Schema

Receives the same JSON schema as shown above (forwarded from Need Agent).

### Response Schema

Returns a JSON quote:

```json
{
  "quote_id": "QUOTE-REQ-1761434743462-j010gfx5m-1729901143",
  "request_id": "REQ-1761434743462-j010gfx5m",
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

### Quote Fields

- **quote_id**: Unique quote identifier
- **supplier_name**: Name of the supplier
- **supplier_location**: Location description
- **supplier_coordinates**: GPS coordinates of supplier
- **status**: "available", "rejected", or "error"
- **coverage_ratio**: Percentage of request that can be fulfilled (0.0-1.0)
- **items_offered**: Array of items with quantities and pricing
- **total_cost**: Total cost in USD
- **distance_km**: Distance from supplier to delivery location
- **estimated_delivery_hours**: Estimated time to delivery
- **estimated_delivery_date**: Formatted delivery date/time
- **delivery_mode**: Delivery method (e.g., "truck")
- **priority**: Priority level from request
- **service_radius_km**: Maximum service distance
- **terms**: Delivery and payment terms
- **valid_until**: Quote expiration timestamp

### Inventory

Current supply agent inventory includes:
- **Blankets**: 500 ea @ $15.00
- **Water Bottles**: 1000 bottles @ $2.00
- **Medical Supplies**: 200 kits @ $50.00
- **Burn Medicine**: 150 kits @ $75.00
- **Food Rations**: 800 meals @ $8.00
- **Tents**: 50 ea @ $200.00
- **Clothing**: 300 sets @ $25.00

## Configuration

### Environment Variables

**Need Agent:**
```bash
export AGENT_SEED_PHRASE="need_agent_berkeley_1_demo_seed"
export AGENT_EXTERNAL_ENDPOINT="https://your-need-agent-url.trycloudflare.com"
export SUPPLY_AGENT_ADDRESS="agent1q..."
export SUPPLY_AGENT_ENDPOINT="http://localhost:8001"
export PORT=8000
```

**Supply Agent:**
```bash
export AGENT_SEED_PHRASE="supply_sf_store_1_demo_seed"
export AGENT_EXTERNAL_ENDPOINT="https://your-supply-agent-url.trycloudflare.com"
export SUPPLIER_LABEL="SF Medical Depot"
export SUPPLIER_LAT="37.7749"
export SUPPLIER_LON="-122.4194"
export PORT=8001
```

## Running the Agents

### Start Supply Agent (Port 8001)
```bash
cd agent-aid/agentaid-marketplace/agents
python supply_agent_chat_adapter.py
```

### Start Need Agent (Port 8000)
```bash
cd agent-aid/agentaid-marketplace/agents
python need_agent_chat_adapter.py
```

### Create Public Tunnels

**Terminal 1 - Need Agent:**
```bash
cloudflared tunnel --url http://localhost:8000
```

**Terminal 2 - Supply Agent:**
```bash
cloudflared tunnel --url http://localhost:8001
```

## Testing

### Test with curl

**Send a need request:**
```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "version": "v1",
    "sender": "test_user",
    "target": "agent_need",
    "session": "test_session",
    "payload": "{\"messages\": [{\"type\": \"text\", \"text\": \"{\\\"items\\\": [\\\"medical supplies\\\", \\\"burn medicine\\\"], \\\"quantity_needed\\\": \\\"100\\\", \\\"location\\\": \\\"San Francisco, CA\\\", \\\"priority\\\": \\\"high\\\", \\\"coordinates\\\": {\\\"latitude\\\": 37.7749, \\\"longitude\\\": -122.4194}, \\\"request_id\\\": \\\"TEST-123\\\"}\"}]}"
  }'
```

### Expected Workflow

1. **User sends request** → Need Agent receives JSON
2. **Need Agent logs** → Shows parsed request details
3. **Need Agent queries** → Sends request to Supply Agent(s)
4. **Supply Agent logs** → Shows quote generation
5. **Supply Agent responds** → Sends JSON quote back
6. **Need Agent evaluates** → Ranks quotes and selects best
7. **Need Agent responds** → Returns formatted recommendation

## Priority Pricing

Supply agents adjust pricing based on priority:
- **Critical**: 10% discount (emergency response)
- **High**: 5% discount
- **Medium**: Standard pricing
- **Low**: 5% premium

## Quote Evaluation Algorithm

Need Agent scores quotes based on:
- **Coverage** (40%): How much of the request can be fulfilled
- **Delivery Time** (30%): Faster delivery gets higher score
- **Cost** (30%): Lower cost gets higher score

## Service Radius

Supply agents only service requests within their configured radius (default: 120 km).
Requests outside the radius are rejected with an explanatory message.

## Integration with Agentverse

Both agents support the Chat Protocol and can be registered on Agentverse:
- Endpoints: `/status`, `/agent_info`, `/` (POST)
- Use `register_need_agent.py` and `register_supply_agent.py` for registration

## Troubleshooting

**No quotes received:**
- Check if supply agent is running
- Verify SUPPLY_AGENT_ENDPOINT is correct in need agent config
- Check if location is within service radius
- Review agent logs for errors

**Invalid JSON errors:**
- Ensure JSON is properly formatted
- Check that coordinates are valid numbers
- Verify all required fields are present

**Connection timeout:**
- Increase httpx timeout in need agent (currently 30s)
- Check network connectivity between agents
- Verify cloudflared tunnels are active

## Dependencies

Make sure to install:
```bash
pip install fastapi uvicorn uagents-core httpx
```

## Next Steps

- Add database integration for real inventory management
- Implement quote acceptance and inventory reservation
- Add delivery tracking and status updates
- Create coordination agent for multi-supplier scenarios
- Add telemetry and analytics
