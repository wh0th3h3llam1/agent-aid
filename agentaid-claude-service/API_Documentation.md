# AgentAid Backend - API Documentation for Fetch.ai Integration

## Backend URL
```
http://localhost:3000
```
*(I'll share production URL when deployed)*

---

## Health Check

**GET** `/health`

Check if backend is running.
```bash
curl http://localhost:3000/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "AgentAid Claude Service",
  "requests_processed": 5,
  "pending_for_agents": 2,
  "chromadb": {
    "total_requests": 5,
    "collection_name": "disaster_requests",
    "embedding_type": "simple_text_based"
  }
}
```

---

## 1. Get Pending Requests

**GET** `/api/uagent/pending-requests`

Your agent polls this endpoint to get new disaster requests.

**Response:**
```json
{
  "success": true,
  "count": 2,
  "requests": [
    {
      "request_id": "REQ-1729876543210-abc123",
      "need_type": "disaster_relief",
      "items": ["tents", "water", "medical supplies"],
      "quantity": {
        "tents": 50,
        "water": 200
      },
      "location": {
        "address": "Main Street Community Center",
        "coordinates": null
      },
      "priority": "high",
      "urgency_level": 3,
      "victim_count": 75,
      "timestamp": "2025-10-25T20:00:00.000Z",
      "contact": null,
      "additional_info": "Building collapsed",
      "status": "pending"
    }
  ]
}
```

**Key Fields:**
- `request_id` - Unique ID (use in all future calls)
- `items` - Array of needed items
- `quantity` - Specific quantities or "low"/"medium"/"high"
- `priority` - "low", "medium", "high", "critical"
- `urgency_level` - Number 1-4 (for sorting)
- `status` - "pending", "processing", "matched", "dispatched", "fulfilled"

---

## 2. Claim a Request

**POST** `/api/uagent/claim-request`

Call this when your agent picks up a request.

**Request:**
```json
{
  "request_id": "REQ-1729876543210-abc123",
  "agent_id": "your_agent_id",
  "agent_address": "agent1q..." // Optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Request claimed by agent",
  "request": {
    "request_id": "REQ-1729876543210-abc123",
    "status": "processing",
    "agent_id": "your_agent_id",
    "processed_at": "2025-10-25T20:05:00.000Z"
  }
}
```

---

## 3. Send Status Updates

**POST** `/api/uagent/update`

Send updates as you process the request.

**Request:**
```json
{
  "request_id": "REQ-1729876543210-abc123",
  "agent_id": "your_agent_id",
  "status": "matched",
  "matched_supplier": {
    "supplier_id": "supply_agent_xyz",
    "name": "Red Cross Bay Area",
    "items": ["tents", "water"],
    "quantity": {"tents": 50, "water": 200}
  },
  "eta": "2025-10-25T22:00:00.000Z"
}
```

**Status Options:**
- `pending` - Waiting
- `processing` - Agent working on it
- `matched` - Supplier found
- `dispatched` - Aid en route
- `fulfilled` - Delivered
- `cancelled` - Cancelled

**Response:**
```json
{
  "success": true,
  "message": "Update received"
}
```

---

## 4. Get Similar Requests (Optional)

**POST** `/api/search/similar`

Get similar past requests (for context/learning).

**Request:**
```json
{
  "query": "medical supplies hospital",
  "limit": 5
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "request_id": "REQ-xxx",
      "similarity_score": 0.87,
      "metadata": {
        "priority": "critical",
        "location": "County Hospital"
      }
    }
  ]
}
```

---

## Expected Flow
```
1. Your agent polls: GET /api/uagent/pending-requests
2. Your agent claims: POST /api/uagent/claim-request
3. Your agent matches with supplier
4. Your agent updates: POST /api/uagent/update (status: "matched")
5. Your agent dispatches aid
6. Your agent updates: POST /api/uagent/update (status: "dispatched")
7. Aid delivered
8. Your agent updates: POST /api/uagent/update (status: "fulfilled")
```

---

## Test Commands
```bash
# Check health
curl http://localhost:3000/health

# Get pending requests
curl http://localhost:3000/api/uagent/pending-requests

# Create test request (so you have something to work with)
curl -X POST http://localhost:3000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"input": "Need 50 tents urgently", "source": "test"}'
```

---

## Questions?

Let me know if you need anything else or want to test the integration together!

My backend is running on: `http://localhost:3000`
```

---

## **📧 Message to Send Your Friend**
```
Hey! My Claude + ChromaDB backend is ready for integration.

📄 See attached: API_DOCUMENTATION.md

🔗 Backend URL: http://localhost:3000

📋 TL;DR:
- Poll: GET /api/uagent/pending-requests
- Claim: POST /api/uagent/claim-request  
- Update: POST /api/uagent/update

✅ Status: Running and tested

Let me know when you're ready to test the integration!