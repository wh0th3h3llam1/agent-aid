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

// Health check
app.get('/health', async (req, res) => {
  const chromaStats = await getStats();
  const pendingCount = getPendingRequests().length;
  
  res.json({ 
    status: 'ok', 
    service: 'AgentAid Claude Service',
    requests_processed: requests.length,
    pending_for_agents: pendingCount,
    chromadb: chromaStats,
    features: {
      followup_system: 'active',
      claude_extraction: 'active',
      chromadb: 'active',
      uagent_integration: 'active'
    }
  });
});

// Main extraction endpoint with intelligent follow-up system
app.post('/api/extract', async (req, res) => {
  try {
    const { input, source, session_id } = req.body;

    if (!input) {
      return res.status(400).json({ error: 'Input text is required' });
    }

    console.log(`📥 Processing ${source || 'text'} input:`, input.substring(0, 100));

    // ========================================
    // FOLLOW-UP RESPONSE HANDLING
    // ========================================
    if (session_id) {
      const session = getSession(session_id);
      
      if (session) {
        console.log(`🔄 Processing follow-up for session: ${session_id}`);
        
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
          
          console.log(`✅ Follow-up completed: ${mergedData.request_id}`);
          console.log(`📦 Available for uAgent pickup`);
          
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
    const structuredData = await extractDisasterData(input);
    
    // ========================================
    // CHECK IF FOLLOW-UP NEEDED
    // ========================================
    const followupCheck = await generateFollowupQuestions(structuredData, input);
    
    if (followupCheck && followupCheck.needs_followup) {
      // Store incomplete data in session for later merge
      storeSession(followupCheck.session_id, {
        original_data: structuredData,
        original_input: input,
        source: source
      });
      
      console.log(`⚠️  Incomplete data detected - requesting follow-up`);
      console.log(`   Completeness Score: ${followupCheck.completeness_score}%`);
      console.log(`   Session ID: ${followupCheck.session_id}`);
      console.log(`   Issues Found: ${followupCheck.issues.length}`);
      
      followupCheck.issues.forEach((issue, index) => {
        console.log(`   ${index + 1}. ${issue.type}: ${issue.field}`);
      });
      
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
    await storeRequest(structuredData);
    requests.push(structuredData);

    // Find similar requests
    const similarRequests = await findSimilarRequests(input, 3);
    
    // Format for uAgent
    const agentPayload = formatForUAgent(structuredData);

    console.log(`✅ Processed ${structuredData.request_id}`);
    console.log(`📦 Available for uAgent pickup`);

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
    console.error('❌ Extraction error:', error);
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

    console.log(`📦 Processing batch of ${inputs.length} requests`);

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
          issues: followupCheck.issues
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

// 🤖 UAGENT ENDPOINTS

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
    
    console.log(`📥 uAgent Update: ${updateData.request_id}`);
    
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

// Search similar requests
app.post('/api/search/similar', async (req, res) => {
  try {
    const { query, limit } = req.body;

    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    const results = await findSimilarRequests(query, limit || 5);

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
    }
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

// Cancel a session (if user wants to start over)
app.post('/api/session/cancel', (req, res) => {
  const { session_id } = req.body;
  
  if (!session_id) {
    return res.status(400).json({ error: 'session_id required' });
  }
  
  const session = getSession(session_id);
  
  if (session) {
    deleteSession(session_id);
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
      has_data: !!session.original_data
    }
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log('\n' + '='.repeat(60));
  console.log('🚀 AgentAid Claude Service');
  console.log('='.repeat(60));
  console.log(`\n📊 Server Status:`);
  console.log(`   Port: ${PORT}`);
  console.log(`   Local: http://localhost:${PORT}`);
  console.log(`   Health: http://localhost:${PORT}/health`);
  console.log(`\n🤖 Fetch.ai Integration:`);
  console.log(`   Pending: http://localhost:${PORT}/api/uagent/pending-requests`);
  console.log(`   Updates: http://localhost:${PORT}/api/uagent/update`);
  console.log(`\n💾 Features:`);
  console.log(`   ✅ Claude Extraction (Sonnet 4.5)`);
  console.log(`   ✅ ChromaDB Vector Search`);
  console.log(`   ✅ Intelligent Follow-up System`);
  console.log(`   ✅ uAgent Integration`);
  console.log(`   ✅ Session Management`);
  console.log('\n' + '='.repeat(60) + '\n');
});