# Agent Features Summary

## ✅ Implemented Features

### 1. **Criticality-Based Response Times**
The agent automatically determines urgency based on supply type:

- **CRITICAL** (30-60 min): Medicine, insulin, oxygen, baby formula
- **HIGH** (2-4 hours): Water, food, shelter, blankets, first aid
- **MEDIUM** (4-8 hours): Clothing, batteries, hygiene items, pet supplies
- **LOW** (8-24 hours): General supplies, comfort items

### 2. **User Profile Management**
- User profile (name, phone, address) stored in browser local storage
- Profile automatically sent to agent when session starts
- Agent has access to user's address and can confirm it
- Agent can update profile information during conversation

### 3. **Address Confirmation Flow**
- Agent ALWAYS confirms delivery address before finalizing request
- Example: "I have your address as 123 Main St. Is this still correct?"
- If user moved or address changed, agent collects new address
- Updates are reflected in the conversation

### 4. **Profile Update Capabilities**
Agent can update:
- **Address**: "What's your current address?"
- **Phone number**: "What's your current phone number?"
- **Name**: "What name should I use?"

### 5. **Smart Supply Request Flow**
1. Greet user with context of their saved profile
2. Ask what supplies they need
3. Collect specific quantities
4. Automatically assess criticality
5. Confirm delivery address
6. Provide timeline based on criticality
7. Ask if they need anything else

## 🔄 Data Flow

```
User Profile (Local Storage)
    ↓
Frontend (useRoom hook)
    ↓
Connection Details API
    ↓
Room Metadata
    ↓
Python Agent (agent.py)
    ↓
Agent has access to: name, phone, address
```

## 📝 Example Conversations

### Critical Supply with Address Confirmation
```
Agent: "Hello! I'm here to help with emergency supplies. What do you need?"
User: "I need insulin"
Agent: "I understand you need insulin. How many doses or vials do you need?"
User: "3 vials"
Agent: "Got it. I have your address as 123 Main St. Is that correct?"
User: "Yes"
Agent: "Perfect. This is emergency priority - help will arrive within 30-60 minutes with 3 vials of insulin. Is there anything else you need?"
```

### Address Update During Request
```
Agent: "Hello! I'm here to help with emergency supplies. What do you need?"
User: "I need water but I moved to a new place"
Agent: "No problem. What's your current address?"
User: "456 Oak Avenue, Apt 2B"
Agent: "I've updated your address to 456 Oak Avenue, Apt 2B. How many people do you need water for?"
User: "5 people for 3 days"
Agent: "Understood. I'm sending water for 5 people for 3 days to 456 Oak Avenue, Apt 2B. High priority - help will arrive within 2-4 hours. Is there anything else you need?"
```

### Phone Number Update
```
User: "Can you update my phone number?"
Agent: "Of course. What's your current phone number?"
User: "+1 555-0199"
Agent: "I've updated your phone number to +1 555-0199. What supplies do you need today?"
```

## 🔧 Technical Implementation

### Frontend Changes
- `hooks/useRoom.ts`: Sends user profile to connection API
- `lib/storage.ts`: Manages user profile in local storage
- `app/api/connection-details/route.ts`: Passes profile as room metadata

### Backend Changes
- `agent.py`: 
  - Reads user profile from room metadata
  - Updated system prompt with criticality levels
  - Address confirmation logic
  - Profile update handling

## 🚀 How to Test

1. **Start the agent:**
   ```bash
   cd livekit
   uv run python agent.py dev
   ```

2. **Start the frontend:**
   ```bash
   cd agent-aid
   pnpm dev
   ```

3. **Test scenarios:**
   - Request critical supply (insulin) → Should say "30-60 minutes"
   - Request water → Should say "2-4 hours"
   - Say "I moved" → Agent should ask for new address
   - Say "update my phone" → Agent should ask for new number

## 📌 Notes

- User profile is stored in browser local storage (key: `disaster_relief_user_profile`)
- Profile is sent to agent via room metadata on every connection
- Agent receives profile in `ctx.room.metadata` as JSON
- Profile updates by agent are conversational only - frontend needs to implement actual storage updates via API
- The agent will ALWAYS confirm address before finalizing any request

## 🔜 Next Steps (Optional Enhancements)

1. **Bidirectional Profile Updates**: Create an API endpoint that the agent can call to actually update the profile in local storage
2. **Request Tracking**: Link agent conversations to supply requests in local storage
3. **Multi-language Support**: Add language detection and translation
4. **Voice Biometrics**: Verify user identity via voice
5. **SMS Notifications**: Send confirmation SMS after request is placed
