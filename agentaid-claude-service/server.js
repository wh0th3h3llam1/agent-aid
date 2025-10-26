import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { extractDisasterData } from './services/claudeService.js';
import { 
  initChromaDB, 
  storeRequest, 
  findSimilarRequests,
  getStats 
} from './services/chromaService.js';
import {
  formatForUAgent,
  getPendingRequests,
  getRequestById,
  getRequestsNearLocation,
  markAsProcessed,
  receiveAgentUpdate,
  getAgentUpdates,
  clearProcessedRequests
} from './services/fetchaiIntegration.js';
import {
  generateFollowupQuestions,
  mergeFollowupResponse,
  storeSession,
  getSession,
  deleteSession
} from './services/followupService.js';
import { 
  geocodeAddress, 
  calculateDistance, 
  findNearestLocation,
  batchGeocode 
} from './services/geocodingService.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// In-memory storage
const requests = [];

// Initialize ChromaDB
await initChromaDB();

// ========================================
// HEALTH & STATUS ENDPOINTS
// ========================================

// Health check
app.get('/health', async (req, res) => {
  const chromaStats = await getStats();
  const pendingCount = getPendingRequests().length;
  
  res.json({ 
    status: 'ok', 
    service: 'AgentAid Claude Service',
    version: '2.0.0',
    requests_processed: requests.length,
    pending_for_agents: pendingCount,
    chromadb: chromaStats,
    features: {
      claude_extraction: 'active',
      followup_system: 'active',
      chromadb_search: 'active',
      geocoding: 'active',
      uagent_integration: 'active',
      session_management: 'active'
    }
  });
});

// Get system statistics
app.get('/api/stats', async (req, res) => {
  try {
    const chromaStats = await getStats();
    const allRequests = requests;
    
    const stats = {
      total_requests: allRequests.length,
      pending_for_agents: getPendingRequests().length,
      by_priority: {
        critical: allRequests.filter(r => r.priority === 'critical').length,
        high: allRequests.filter(r => r.priority === 'high').length,
        medium: allRequests.filter(r => r.priority === 'medium').length,
        low: allRequests.filter(r => r.priority === 'low').length
      },
      geocoded_requests: allRequests.filter(r => r.coordinates).length,
      chromadb: chromaStats,
      uptime: process.uptime(),
      memory_usage: process.memoryUsage()
    };
    
    res.json({
      success: true,
      stats: stats
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// ========================================
// MAIN EXTRACTION ENDPOINTS
// ========================================

// Main extraction endpoint with intelligent follow-up system and geocoding
app.post('/api/extract', async (req, res) => {
  try {
    const { input, source, session_id } = req.body;

    if (!input) {
      return res.status(400).json({ error: 'Input text is required' });
    }

    console.log(`\n${'='.repeat(80)}`);
    console.log(`📥 Processing ${source || 'text'} input`);
    console.log(`   Input: ${input.substring(0, 100)}${input.length > 100 ? '...' : ''}`);
    console.log('='.repeat(80));

    // ========================================
    // FOLLOW-UP RESPONSE HANDLING
    // ========================================
    if (session_id) {
      const session = getSession(session_id);
      
      if (session) {
        console.log(`\n🔄 Processing follow-up for session: ${session_id}`);
        
        try {
          // Merge follow-up response with original data
          const mergedData = await mergeFollowupResponse(
            session.original_data,
            input,
            session_id
          );
          
          // Store merged data
          await storeRequest(mergedData);
          requests.push(mergedData);
          
          // Find similar requests
          const similarRequests = await findSimilarRequests(input, 3);
          
          // Format for uAgent
          const agentPayload = formatForUAgent(mergedData);
          
          // Clean up session
          deleteSession(session_id);
          
          console.log(`\n✅ Follow-up completed: ${mergedData.request_id}`);
          console.log(`   Items: ${mergedData.items.join(', ')}`);
          console.log(`   Location: ${mergedData.location}`);
          if (mergedData.coordinates) {
            console.log(`   Coordinates: ${mergedData.coordinates.latitude}, ${mergedData.coordinates.longitude}`);
          }
          console.log(`   Priority: ${mergedData.priority}`);
          console.log(`📦 Available for uAgent pickup`);
          console.log('='.repeat(80) + '\n');
          
          return res.json({
            success: true,
            data: mergedData,
            similar_requests: similarRequests,
            agent_payload: agentPayload,
            message: 'Follow-up complete. Request processed and ready for agents.',
            follow_up_completed: true,
            needs_followup: false
          });
          
        } catch (error) {
          console.error('❌ Error merging follow-up:', error);
          // If merge fails, treat as new request
          deleteSession(session_id);
        }
      } else {
        console.log(`⚠️  Session ${session_id} not found or expired`);
      }
    }

    // ========================================
    // INITIAL EXTRACTION
    // ========================================
    console.log('\n🤖 Claude extracting data...');
    const structuredData = await extractDisasterData(input);
    
    console.log('✅ Extraction complete');
    console.log(`   Items: ${structuredData.items.join(', ')}`);
    console.log(`   Location: ${structuredData.location || 'Not provided'}`);
    if (structuredData.coordinates) {
      console.log(`   Coordinates: ${structuredData.coordinates.latitude}, ${structuredData.coordinates.longitude}`);
    }
    console.log(`   Contact: ${structuredData.contact || 'Not provided'}`);
    
    // ========================================
    // CHECK IF FOLLOW-UP NEEDED
    // ========================================
    console.log('\n🔍 Checking completeness...');
    const followupCheck = await generateFollowupQuestions(structuredData, input);
    
    if (followupCheck && followupCheck.needs_followup) {
      // Store incomplete data in session for later merge
      storeSession(followupCheck.session_id, {
        original_data: structuredData,
        original_input: input,
        source: source
      });
      
      console.log(`\n⚠️  Incomplete data detected - requesting follow-up`);
      console.log(`   Completeness Score: ${followupCheck.completeness_score}%`);
      console.log(`   Session ID: ${followupCheck.session_id}`);
      console.log(`   Issues Found: ${followupCheck.issues.length}`);
      
      followupCheck.issues.forEach((issue, index) => {
        console.log(`   ${index + 1}. ${issue.type}: ${issue.field}`);
      });
      console.log('='.repeat(80) + '\n');
      
      return res.json({
        success: true,
        needs_followup: true,
        session_id: followupCheck.session_id,
        completeness_score: followupCheck.completeness_score,
        partial_data: structuredData,
        issues: followupCheck.issues,
        followup_message: followupCheck.followup_message,
        message: 'Additional information needed to complete request'
      });
    }
    
    // ========================================
    // DATA IS COMPLETE - PROCESS NORMALLY
    // ========================================
    console.log(`✅ Data is complete (100%)`);
    
    await storeRequest(structuredData);
    requests.push(structuredData);

    // Find similar requests
    const similarRequests = await findSimilarRequests(input, 3);
    
    // Format for uAgent
    const agentPayload = formatForUAgent(structuredData);

    console.log(`\n✅ Processed ${structuredData.request_id}`);
    console.log(`📦 Available for uAgent pickup`);
    
    // ========================================
    // SEND TO NEED AGENT (if running locally)
    // ========================================
    const NEED_AGENT_URL = process.env.NEED_AGENT_URL || 'http://localhost:8000/simple';
    try {
      console.log(`\n📤 Sending to Need Agent at ${NEED_AGENT_URL}...`);
      
      const needAgentMessage = `${input}`;  // Send original user message
      
      const needAgentResponse = await fetch(NEED_AGENT_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender: 'chat_ui_user',
          message: needAgentMessage
        })
      });
      
      if (needAgentResponse.ok) {
        const result = await needAgentResponse.json();
        console.log(`✅ Request forwarded to Need Agent: ${result.status}`);
      } else {
        console.log(`⚠️  Need Agent returned: ${needAgentResponse.status}`);
      }
    } catch (needAgentError) {
      console.log(`⚠️  Could not reach Need Agent (may be on Agentverse): ${needAgentError.message}`);
    }
    
    console.log('='.repeat(80) + '\n');

    res.json({
      success: true,
      data: structuredData,
      similar_requests: similarRequests,
      agent_payload: agentPayload,
      message: 'Request ready for Fetch.ai uAgent',
      needs_followup: false,
      completeness_score: 100
    });

  } catch (error) {
    console.error('\n❌ Extraction error:', error);
    console.log('='.repeat(80) + '\n');
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Batch processing
app.post('/api/extract/batch', async (req, res) => {
  try {
    const { inputs } = req.body;

    if (!Array.isArray(inputs)) {
      return res.status(400).json({ error: 'Inputs must be an array' });
    }

    console.log(`\n📦 Processing batch of ${inputs.length} requests`);

    const results = [];
    const followupsNeeded = [];

    for (const input of inputs) {
      const data = await extractDisasterData(input);
      const followupCheck = await generateFollowupQuestions(data, input);
      
      if (followupCheck && followupCheck.needs_followup) {
        // Track items needing follow-up
        followupsNeeded.push({
          input: input,
          session_id: followupCheck.session_id,
          issues: followupCheck.issues,
          completeness_score: followupCheck.completeness_score
        });
        
        storeSession(followupCheck.session_id, {
          original_data: data,
          original_input: input
        });
      } else {
        // Complete data - store it
        await storeRequest(data);
        requests.push(data);
        const agentPayload = formatForUAgent(data);
        results.push({ data, agentPayload });
      }
    }

    console.log(`✅ Batch complete: ${results.length} processed, ${followupsNeeded.length} need follow-up\n`);

    res.json({
      success: true,
      processed: results.length,
      needs_followup: followupsNeeded.length,
      data: results,
      followup_required: followupsNeeded
    });

  } catch (error) {
    console.error('❌ Batch extraction error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// ========================================
// UAGENT ENDPOINTS
// ========================================

// Get all pending requests (your friend's agent polls this)
app.get('/api/uagent/pending-requests', (req, res) => {
  const pending = getPendingRequests();
  
  res.json({
    success: true,
    count: pending.length,
    requests: pending
  });
});

// Get specific request for agent
app.get('/api/uagent/request/:id', (req, res) => {
  const request = getRequestById(req.params.id);
  
  if (!request) {
    return res.status(404).json({ 
      success: false,
      error: 'Request not found' 
    });
  }

  res.json({
    success: true,
    request: request
  });
});

// Get requests near a location (for agents to find nearby needs)
app.post('/api/uagent/requests-nearby', (req, res) => {
  try {
    const { latitude, longitude, radius_km } = req.body;
    
    if (!latitude || !longitude) {
      return res.status(400).json({
        error: 'latitude and longitude required'
      });
    }
    
    const nearbyRequests = getRequestsNearLocation(
      parseFloat(latitude),
      parseFloat(longitude),
      parseFloat(radius_km) || 10
    );
    
    console.log(`📍 Nearby search: ${nearbyRequests.length} requests within ${radius_km || 10}km`);
    
    res.json({
      success: true,
      count: nearbyRequests.length,
      search_location: { 
        latitude: parseFloat(latitude), 
        longitude: parseFloat(longitude) 
      },
      radius_km: parseFloat(radius_km) || 10,
      requests: nearbyRequests
    });
    
  } catch (error) {
    console.error('Nearby search error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Agent confirms pickup of request
app.post('/api/uagent/claim-request', (req, res) => {
  const { request_id, agent_id, agent_address } = req.body;

  if (!request_id || !agent_id) {
    return res.status(400).json({ 
      error: 'request_id and agent_id required' 
    });
  }

  const updated = markAsProcessed(request_id, { agent_id, agent_address });

  if (!updated) {
    return res.status(404).json({ error: 'Request not found' });
  }

  console.log(`✅ Request claimed: ${request_id} by ${agent_id}`);

  res.json({
    success: true,
    message: 'Request claimed by agent',
    request: updated
  });
});

// Receive status updates from uAgent
app.post('/api/uagent/update', (req, res) => {
  try {
    const updateData = req.body;
    
    console.log(`\n📥 uAgent Update: ${updateData.request_id}`);
    console.log(`   Agent: ${updateData.agent_id}`);
    console.log(`   Status: ${updateData.status}`);
    
    if (updateData.matched_supplier) {
      console.log(`   Supplier: ${updateData.matched_supplier.name}`);
    }
    
    const result = receiveAgentUpdate(updateData);

    res.json({
      success: true,
      message: 'Update received'
    });

  } catch (error) {
    console.error('Update error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get all agent updates history
app.get('/api/uagent/updates', (req, res) => {
  const updates = getAgentUpdates();
  
  res.json({
    success: true,
    count: updates.length,
    updates: updates
  });
});

// Cleanup completed requests
app.post('/api/uagent/cleanup', (req, res) => {
  const cleared = clearProcessedRequests();
  
  res.json({
    success: true,
    message: `Cleared ${cleared} completed requests`
  });
});

// ========================================
// GEOCODING ENDPOINTS
// ========================================

// Geocode a single address
app.post('/api/geocode', async (req, res) => {
  try {
    const { address } = req.body;
    
    if (!address) {
      return res.status(400).json({ error: 'Address is required' });
    }
    
    console.log(`🌍 Geocoding request: "${address}"`);
    
    const result = await geocodeAddress(address);
    
    if (result) {
      console.log(`✅ Geocoded: ${result.latitude}, ${result.longitude}`);
      res.json({
        success: true,
        geocoded: result
      });
    } else {
      console.log(`⚠️  Could not geocode: "${address}"`);
      res.status(404).json({
        success: false,
        error: 'Could not geocode address'
      });
    }
  } catch (error) {
    console.error('Geocoding error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Batch geocode multiple addresses
app.post('/api/geocode/batch', async (req, res) => {
  try {
    const { addresses } = req.body;
    
    if (!Array.isArray(addresses)) {
      return res.status(400).json({ error: 'addresses must be an array' });
    }
    
    console.log(`🌍 Batch geocoding ${addresses.length} addresses`);
    
    const results = await batchGeocode(addresses);
    
    res.json({
      success: true,
      count: results.length,
      results: results
    });
    
  } catch (error) {
    console.error('Batch geocoding error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Calculate distance between two coordinates
app.post('/api/distance', (req, res) => {
  try {
    const { lat1, lon1, lat2, lon2 } = req.body;
    
    if (!lat1 || !lon1 || !lat2 || !lon2) {
      return res.status(400).json({
        error: 'All coordinates required: lat1, lon1, lat2, lon2'
      });
    }
    
    const distance = calculateDistance(
      parseFloat(lat1),
      parseFloat(lon1),
      parseFloat(lat2),
      parseFloat(lon2)
    );
    
    res.json({
      success: true,
      distance_km: distance,
      distance_miles: distance * 0.621371
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// ========================================
// SEARCH ENDPOINTS
// ========================================

// Search similar requests
app.post('/api/search/similar', async (req, res) => {
  try {
    const { query, limit } = req.body;

    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    console.log(`🔍 Similarity search: "${query}"`);

    const results = await findSimilarRequests(query, limit || 5);

    console.log(`   Found ${results.length} similar requests`);

    res.json({
      success: true,
      query: query,
      results: results
    });

  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// ========================================
// REQUEST MANAGEMENT ENDPOINTS
// ========================================

// Get all requests
app.get('/api/requests', (req, res) => {
  res.json({
    success: true,
    data: requests,
    total: requests.length,
    by_priority: {
      critical: requests.filter(r => r.priority === 'critical').length,
      high: requests.filter(r => r.priority === 'high').length,
      medium: requests.filter(r => r.priority === 'medium').length,
      low: requests.filter(r => r.priority === 'low').length
    },
    geocoded: requests.filter(r => r.coordinates).length
  });
});

// Get specific request
app.get('/api/requests/:id', (req, res) => {
  const request = requests.find(r => r.request_id === req.params.id);
  
  if (!request) {
    return res.status(404).json({ error: 'Request not found' });
  }

  res.json({
    success: true,
    data: request
  });
});

// Get requests by priority (useful for dashboards)
app.get('/api/requests/priority/:priority', (req, res) => {
  const priority = req.params.priority.toLowerCase();
  const filtered = requests.filter(r => r.priority === priority);
  
  res.json({
    success: true,
    priority: priority,
    count: filtered.length,
    data: filtered
  });
});

// Delete a specific request
app.delete('/api/requests/:id', (req, res) => {
  const index = requests.findIndex(r => r.request_id === req.params.id);
  
  if (index === -1) {
    return res.status(404).json({ error: 'Request not found' });
  }
  
  const deleted = requests.splice(index, 1)[0];
  console.log(`🗑️  Deleted request: ${deleted.request_id}`);
  
  res.json({
    success: true,
    message: 'Request deleted',
    deleted: deleted
  });
});

// ========================================
// SESSION MANAGEMENT ENDPOINTS
// ========================================

// Get session info (for debugging)
app.get('/api/session/:session_id', (req, res) => {
  const session = getSession(req.params.session_id);
  
  if (!session) {
    return res.status(404).json({
      success: false,
      error: 'Session not found or expired'
    });
  }
  
  res.json({
    success: true,
    session: {
      session_id: req.params.session_id,
      created_at: session.created_at,
      expires_at: session.expires_at,
      has_data: !!session.original_data,
      original_input: session.original_input
    }
  });
});

// Cancel a session (if user wants to start over)
app.post('/api/session/cancel', (req, res) => {
  const { session_id } = req.body;
  
  if (!session_id) {
    return res.status(400).json({ error: 'session_id required' });
  }
  
  const session = getSession(session_id);
  
  if (session) {
    deleteSession(session_id);
    console.log(`🗑️  Session cancelled: ${session_id}`);
    res.json({
      success: true,
      message: 'Session cancelled'
    });
  } else {
    res.status(404).json({
      success: false,
      error: 'Session not found or already expired'
    });
  }
});

// ========================================
// START SERVER
// ========================================

app.listen(PORT, '0.0.0.0', () => {
  console.log('\n' + '█'.repeat(80));
  console.log('█' + ' '.repeat(78) + '█');
  console.log('█' + '  🚨 AGENTAID - DISASTER RESPONSE SYSTEM'.padEnd(78) + '█');
  console.log('█' + '  Powered by Claude Sonnet 4.5 + Fetch.ai'.padEnd(78) + '█');
  console.log('█' + ' '.repeat(78) + '█');
  console.log('█'.repeat(80));
  
  console.log('\n📊 SERVER STATUS:');
  console.log(`   Port: ${PORT}`);
  console.log(`   Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`   Local: http://localhost:${PORT}`);
  console.log(`   Network: http://0.0.0.0:${PORT}`);
  
  console.log('\n🔗 KEY ENDPOINTS:');
  console.log(`   Health Check: http://localhost:${PORT}/health`);
  console.log(`   Extract: POST http://localhost:${PORT}/api/extract`);
  console.log(`   Geocode: POST http://localhost:${PORT}/api/geocode`);
  
  console.log('\n🤖 FETCH.AI INTEGRATION:');
  console.log(`   Pending: GET http://localhost:${PORT}/api/uagent/pending-requests`);
  console.log(`   Nearby: POST http://localhost:${PORT}/api/uagent/requests-nearby`);
  console.log(`   Claim: POST http://localhost:${PORT}/api/uagent/claim-request`);
  console.log(`   Update: POST http://localhost:${PORT}/api/uagent/update`);
  
  console.log('\n💾 FEATURES ENABLED:');
  console.log('   ✅ Claude Sonnet 4.5 Extraction');
  console.log('   ✅ Intelligent Follow-up System');
  console.log('   ✅ ChromaDB Vector Search');
  console.log('   ✅ Geocoding & Coordinates');
  console.log('   ✅ Session Management');
  console.log('   ✅ uAgent Integration');
  console.log('   ✅ Multilingual Support');
  console.log('   ✅ Priority-based Routing');
  
  console.log('\n🎯 READY FOR DEMO!');
  console.log('█'.repeat(80) + '\n');
});