# Disaster Relief Helpline - Integration Guide

## Overview
This application is a disaster management agent service that allows users to request emergency supplies via voice or text. The system collects user information, processes requests through an AI agent, and integrates with a backend for fulfillment.

## Key Features

### 1. User Profile Management
- **First-time users** are prompted to provide:
  - Phone number (required)
  - Address (required)
  - Name (optional)
- Information is stored in browser's local storage
- Users can edit their information anytime

### 2. Supply Request Flow
1. User clicks "Request Help Now" button
2. Agent greets and asks what supplies are needed
3. Agent collects:
   - Supply type (food, water, medicine, etc.)
   - Quantity (asks if not specified)
   - Confirms phone number and address
4. Request is saved to local storage and sent to backend API
5. User receives confirmation with estimated delivery time

### 3. Request History
- All requests are stored locally
- Users can view their request history from the welcome screen
- Shows status: pending, processing, fulfilled, cancelled
- Displays timestamp, supply type, quantity, and contact info

### 4. Active Request Banner
- During a session, shows the current/latest request status
- Animates for pending/processing requests
- Auto-updates every 3 seconds

## Integration Points

### Backend API Integration (`/app/api/save-request/route.ts`)

**Current State:** Placeholder implementation

**To Integrate:**
Replace the `processSupplyRequest` function with your actual backend call:

```typescript
async function processSupplyRequest(payload: SupplyRequestPayload) {
  // Replace this with your Claude agent backend integration
  const response = await fetch('YOUR_BACKEND_URL/api/requests', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_API_KEY',
    },
    body: JSON.stringify(payload),
  });
  
  if (!response.ok) {
    throw new Error('Backend request failed');
  }
  
  return response.json();
}
```

**Expected Payload:**
```typescript
{
  supplyType: string;      // e.g., "Water", "Food", "Medicine"
  quantity: number;        // e.g., 10, 50, 100
  requestText: string;     // Original user request
  phoneNumber: string;     // User's phone
  address: string;         // User's address
  urgency?: 'low' | 'medium' | 'high' | 'critical';
}
```

**Expected Response:**
```typescript
{
  requestId: string;       // Unique request ID
  estimatedTime: string;   // e.g., "2-4 hours"
  status: string;          // e.g., "pending"
}
```

### Claude Agent Integration

The LiveKit agent (`agent.py`) is configured to:
1. Collect supply requests via voice/text
2. Extract structured information (type, quantity, urgency)
3. Confirm details with the user

**To integrate with Claude:**
You need to create a middleware that:
1. Receives the conversation transcript from LiveKit
2. Sends it to Claude for JSON extraction
3. Calls the `/api/save-request` endpoint with structured data

**Example Claude Prompt:**
```
Extract the following from this disaster relief request:
- supplyType: type of supply needed
- quantity: specific amount
- urgency: low/medium/high/critical

Request: "{user_message}"

Return as JSON.
```

### Agent Instructions (`agent.py`)

The agent is programmed to:
- Ask for quantity if not specified
- Confirm phone number and address
- Provide reassurance and estimated times
- Handle vague requests (e.g., "my family needs insulin" → asks "how many units?")

**Customization:**
Edit the `instructions` parameter in `agent.py` to adjust the agent's behavior.

## Local Storage Schema

### User Profile
```typescript
{
  phoneNumber: string;
  address: string;
  name?: string;
}
```
**Storage Key:** `disaster_relief_user_profile`

### Supply Requests
```typescript
{
  id: string;              // Auto-generated
  timestamp: number;       // Unix timestamp
  supplyType: string;
  quantity: number;
  status: 'pending' | 'processing' | 'fulfilled' | 'cancelled';
  requestText: string;
  phoneNumber: string;
  address: string;
}
```
**Storage Key:** `disaster_relief_requests`

## Files Modified/Created

### Frontend (agent-aid/)
- `app-config.ts` - Updated branding and colors
- `components/app/welcome-view.tsx` - User info collection + request history
- `components/app/session-view.tsx` - Added active request banner
- `components/app/request-history.tsx` - Request history component
- `components/app/active-request-banner.tsx` - Live request status
- `lib/storage.ts` - Local storage utilities
- `hooks/useSupplyRequest.ts` - Request submission hook
- `app/api/save-request/route.ts` - API endpoint (placeholder)

### Backend (livekit/)
- `agent.py` - Updated agent instructions for disaster relief

## Running the Application

### 1. Start the Agent (Backend)
```bash
cd livekit
uv run python agent.py dev
```

### 2. Start the Frontend
```bash
cd agent-aid
pnpm dev
```

### 3. Access the Application
Open http://localhost:3000

## Testing Flow

1. **First Visit:**
   - Enter phone number and address
   - Click "Save & Continue"

2. **Make a Request:**
   - Click "Request Help Now"
   - Speak or type: "I need water for 5 people"
   - Agent will confirm and process

3. **View History:**
   - Click "View Request History" on welcome screen
   - See all past requests with status

4. **During Session:**
   - Active request banner shows at top
   - Chat transcript available
   - Both voice and text input work

## Next Steps

1. **Integrate Claude Agent:**
   - Set up Claude API endpoint
   - Create middleware to process transcripts
   - Extract structured JSON from conversations

2. **Connect Backend:**
   - Replace placeholder in `/api/save-request/route.ts`
   - Add authentication
   - Implement request fulfillment workflow

3. **Add Notifications:**
   - SMS confirmations
   - Status updates
   - Delivery notifications

4. **Database Integration:**
   - Move from local storage to database
   - Sync across devices
   - Admin dashboard for request management

## Support

For issues or questions, check:
- LiveKit Docs: https://docs.livekit.io/agents/
- Claude API Docs: https://docs.anthropic.com/
