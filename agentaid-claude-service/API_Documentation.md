# AgentAid API Documentation - Fetch.ai Integration

## Backend URL
```
http://localhost:3000
```

## Core Endpoints

### 1. Get Pending Requests
**Endpoint:** `GET /api/uagent/pending-requests`

**Description:** Poll this every 10 seconds to get new disaster requests.

**Response Fields:**
- `request_id` - Unique identifier
- `items` - Array of needed items
- `quantity` - Object with specific quantities
- `location.address` - Text address
- `location.coordinates.latitude` - Decimal degrees
- `location.coordinates.longitude` - Decimal degrees
- `priority` - "low", "medium", "high", "critical"
- `urgency_level` - Number 1-4
- `status` - "pending", "processing", "matched", "dispatched", "fulfilled"
- `geocoded` - Boolean, true if coordinates available
- `victim_count` - Number of people affected
- `contact` - Phone number or contact info

---

### 2. Get Nearby Requests
**Endpoint:** `POST /api/uagent/requests-nearby`

**Request Body:**
```json
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "radius_km": 50
}
```

**Description:** Find requests within specified radius. Returns results sorted by distance.

**Response:** Same as pending requests, plus `distance_km` field.

---

### 3. Claim a Request
**Endpoint:** `POST /api/uagent/claim-request`

**Request Body:**
```json
{
  "request_id": "REQ-xxx",
  "agent_id": "your_agent_id",
  "agent_address": "agent1q..."
}
```

**Description:** Call when your agent picks up a request.

---

### 4. Send Status Updates
**Endpoint:** `POST /api/uagent/update`

**Request Body:**
```json
{
  "request_id": "REQ-xxx",
  "agent_id": "your_agent_id",
  "status": "matched",
  "matched_supplier": {
    "supplier_id": "supply_xxx",
    "name": "Supplier Name"
  },
  "eta": "2025-10-25T22:00:00.000Z"
}
```

**Status Values:**
- `pending` - Waiting
- `processing` - Agent working
- `matched` - Supplier found
- `dispatched` - Aid en route
- `fulfilled` - Delivered
- `cancelled` - Cancelled

---

### 5. Calculate Distance
**Endpoint:** `POST /api/distance`

**Request Body:**
```json
{
  "lat1": 37.7749,
  "lon1": -122.4194,
  "lat2": 37.8044,
  "lon2": -122.2712
}
```

**Response:** Distance in kilometers and miles.

---

### 6. Get Specific Request
**Endpoint:** `GET /api/uagent/request/:id`

**Description:** Get details for a specific request by ID.

---

### 7. Health Check
**Endpoint:** `GET /health`

**Description:** Check if backend is running.

---

## Integration Workflow
```
1. Poll: GET /api/uagent/pending-requests
2. Claim: POST /api/uagent/claim-request
3. [Your matching logic]
4. Update: POST /api/uagent/update (status: "matched")
5. Update: POST /api/uagent/update (status: "dispatched")
6. Update: POST /api/uagent/update (status: "fulfilled")
```



## Testing Commands
```bash
# Check backend
curl http://localhost:3000/health

# Get pending requests
curl http://localhost:3000/api/uagent/pending-requests

# Create test request
curl -X POST http://localhost:3000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"input": "Need 50 tents at Main Street. Contact: 555-1234", "source": "test"}'

# Test nearby search
curl -X POST http://localhost:3000/api/uagent/requests-nearby \
  -H "Content-Type: application/json" \
  -d '{"latitude": 37.7749, "longitude": -122.4194, "radius_km": 50}'
```

## Important Notes

- Poll every 10 seconds (not faster than 5s, not slower than 30s)
- Always check if `coordinates` exist before using them
- Use `geocoded: true` to verify coordinates are available
- `urgency_level` is numeric (1-4) for sorting priority
- All timestamps are in ISO 8601 format
- Requests are sorted by distance in nearby search

## Checklist

- [ ] Agent can connect to `/health`
- [ ] Agent can poll `/api/uagent/pending-requests`
- [ ] Agent can claim requests
- [ ] Agent can send status updates
- [ ] Agent uses coordinates for routing
- [ ] Tested end-to-end flow

## Contact

Ready to integrate! Let's test together when you're ready.