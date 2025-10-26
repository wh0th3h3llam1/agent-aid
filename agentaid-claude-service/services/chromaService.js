/**
 * ChromaDB Service - In-Memory Vector Storage
 * Simplified version for disaster request storage and similarity search
 */

// In-memory storage for requests
let requestsDB = [];
let isInitialized = false;

/**
 * Initialize ChromaDB (in-memory version)
 */
export async function initChromaDB() {
  if (isInitialized) {
    return;
  }
  
  console.log('📊 Initializing ChromaDB (in-memory)...');
  requestsDB = [];
  isInitialized = true;
  console.log('✅ ChromaDB initialized');
}

/**
 * Store a disaster request
 */
export async function storeRequest(requestData) {
  try {
    const request = {
      id: requestData.request_id || `REQ-${Date.now()}`,
      ...requestData,
      stored_at: new Date().toISOString()
    };
    
    requestsDB.push(request);
    
    console.log(`✅ Stored request: ${request.id}`);
    return { success: true, id: request.id };
  } catch (error) {
    console.error('❌ Error storing request:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Find similar requests (simple keyword matching)
 */
export async function findSimilarRequests(query, limit = 5) {
  try {
    if (!query || typeof query !== 'string') {
      return [];
    }
    
    const queryLower = query.toLowerCase();
    const keywords = queryLower.split(' ').filter(w => w.length > 3);
    
    // Score each request based on keyword matches
    const scored = requestsDB.map(req => {
      let score = 0;
      const reqText = JSON.stringify(req).toLowerCase();
      
      keywords.forEach(keyword => {
        if (reqText.includes(keyword)) {
          score++;
        }
      });
      
      return { request: req, score };
    });
    
    // Sort by score and return top matches
    const results = scored
      .filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map(item => item.request);
    
    return results;
  } catch (error) {
    console.error('❌ Error finding similar requests:', error);
    return [];
  }
}

/**
 * Get statistics
 */
export async function getStats() {
  return {
    total_requests: requestsDB.length,
    collection_name: 'disaster_requests',
    embedding_type: 'simple_text_based',
    storage_mode: 'in-memory'
  };
}

/**
 * Clear all requests (for testing)
 */
export async function clearAllRequests() {
  const count = requestsDB.length;
  requestsDB = [];
  console.log(`🗑️  Cleared ${count} requests`);
  return { success: true, cleared: count };
}

/**
 * Get all requests
 */
export function getAllRequests() {
  return requestsDB;
}

/**
 * Get request by ID
 */
export function getRequestById(id) {
  return requestsDB.find(req => req.id === id || req.request_id === id);
}
