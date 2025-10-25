import dotenv from 'dotenv';

dotenv.config();

// Store for agent communication
const pendingRequests = new Map();
const agentUpdates = new Map();

// Format data for uAgent consumption
export function formatForUAgent(structuredData) {
  // Create a clean payload that uAgents can process
  const payload = {
    request_id: structuredData.request_id,
    need_type: 'disaster_relief',
    items: structuredData.items,
    quantity: structuredData.quantity_needed,
    location: {
      address: structuredData.location,
      coordinates: null // Your friend can add geocoding later
    },
    priority: structuredData.priority,
    urgency_level: getPriorityScore(structuredData.priority),
    victim_count: structuredData.victim_count || 0,
    timestamp: structuredData.timestamp,
    contact: structuredData.contact,
    additional_info: structuredData.additional_notes,
    status: 'pending'
  };

  console.log(`📦 Formatted for uAgent: ${payload.request_id}`);
  
  // Store it for agent pickup
  pendingRequests.set(payload.request_id, payload);
  
  return payload;
}

// Convert priority to numerical score for agent decision-making
function getPriorityScore(priority) {
  const scores = {
    'critical': 4,
    'high': 3,
    'medium': 2,
    'low': 1
  };
  return scores[priority] || 2;
}

// Get pending requests (your friend's agent will poll this)
export function getPendingRequests() {
  return Array.from(pendingRequests.values());
}

// Get specific request by ID
export function getRequestById(requestId) {
  return pendingRequests.get(requestId);
}

// Mark request as processed by agent
export function markAsProcessed(requestId, agentData) {
  const request = pendingRequests.get(requestId);
  if (request) {
    request.status = 'processing';
    request.agent_id = agentData.agent_id;
    request.processed_at = new Date().toISOString();
    
    console.log(`✅ Request ${requestId} picked up by agent ${agentData.agent_id}`);
  }
  return request;
}

// Receive updates from uAgent
export function receiveAgentUpdate(updateData) {
  const { request_id, agent_id, status, matched_supplier, eta } = updateData;
  
  console.log(`📥 Agent Update: ${request_id}`);
  console.log(`   Status: ${status}`);
  
  // Update the request
  const request = pendingRequests.get(request_id);
  if (request) {
    request.status = status;
    request.last_updated = new Date().toISOString();
    
    if (matched_supplier) {
      request.matched_supplier = matched_supplier;
      console.log(`   ✅ Matched: ${matched_supplier.name}`);
    }
    
    if (eta) {
      request.eta = eta;
    }
  }
  
  // Store in updates history
  agentUpdates.set(Date.now(), {
    ...updateData,
    received_at: new Date().toISOString()
  });
  
  return { success: true, message: 'Update received' };
}

// Get all agent updates
export function getAgentUpdates() {
  return Array.from(agentUpdates.values());
}

// Clear processed requests (cleanup)
export function clearProcessedRequests() {
  const cleared = [];
  for (const [id, request] of pendingRequests.entries()) {
    if (request.status === 'fulfilled' || request.status === 'cancelled') {
      cleared.push(id);
      pendingRequests.delete(id);
    }
  }
  console.log(`🧹 Cleared ${cleared.length} completed requests`);
  return cleared.length;
}