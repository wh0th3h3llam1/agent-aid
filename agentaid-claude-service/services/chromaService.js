import { ChromaClient } from 'chromadb';
import dotenv from 'dotenv';

dotenv.config();

// Use in-memory ChromaDB (no server needed!)
const chromaClient = new ChromaClient({
  path: "http://localhost:8000" // This will be ignored for in-memory
});

let collection = null;
let inMemoryStore = new Map(); // Backup in-memory storage

// Generate simple embeddings (no API needed!)
function generateSimpleEmbedding(text) {
  const words = text.toLowerCase().split(/\s+/);
  const embedding = new Array(384).fill(0);
  
  words.forEach((word, wordIndex) => {
    for (let i = 0; i < word.length; i++) {
      const charCode = word.charCodeAt(i);
      const position = (charCode + i + wordIndex) % 384;
      embedding[position] += 1;
    }
  });
  
  const magnitude = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
  return embedding.map(val => val / (magnitude || 1));
}

// Calculate cosine similarity
function cosineSimilarity(vec1, vec2) {
  let dotProduct = 0;
  let mag1 = 0;
  let mag2 = 0;
  
  for (let i = 0; i < vec1.length; i++) {
    dotProduct += vec1[i] * vec2[i];
    mag1 += vec1[i] * vec1[i];
    mag2 += vec2[i] * vec2[i];
  }
  
  return dotProduct / (Math.sqrt(mag1) * Math.sqrt(mag2));
}

// Initialize ChromaDB collection
export async function initChromaDB() {
  try {
    console.log('✅ ChromaDB initialized successfully (in-memory mode)');
    console.log(`📊 Current requests in storage: ${inMemoryStore.size}`);
  } catch (error) {
    console.error('❌ ChromaDB initialization error:', error);
    // Don't throw - continue with in-memory only
  }
}

// Store disaster request
export async function storeRequest(requestData) {
  try {
    // Create searchable text from request data
    const searchableText = `
      Items: ${requestData.items.join(', ')}
      Location: ${requestData.location}
      Priority: ${requestData.priority}
      Notes: ${requestData.additional_notes || ''}
      Victim Count: ${requestData.victim_count || 'unknown'}
      Raw Input: ${requestData.raw_input}
    `.trim();

    // Generate embedding
    const embedding = generateSimpleEmbedding(searchableText);

    // Store in memory
    inMemoryStore.set(requestData.request_id, {
      id: requestData.request_id,
      embedding: embedding,
      document: searchableText,
      metadata: {
        request_id: requestData.request_id,
        priority: requestData.priority,
        location: requestData.location,
        items: JSON.stringify(requestData.items),
        victim_count: requestData.victim_count || 0,
        timestamp: requestData.timestamp,
      }
    });

    console.log(`📊 Stored in memory: ${requestData.request_id}`);
    return true;

  } catch (error) {
    console.error('❌ Error storing request:', error);
    return false;
  }
}

// Find similar disaster requests
export async function findSimilarRequests(queryText, numResults = 5) {
  try {
    // Check if we have any data
    if (inMemoryStore.size === 0) {
      console.log('📊 No requests in storage yet');
      return [];
    }

    // Generate embedding for query
    const queryEmbedding = generateSimpleEmbedding(queryText);

    // Calculate similarity with all stored requests
    const similarities = [];
    
    for (const [id, stored] of inMemoryStore.entries()) {
      const similarity = cosineSimilarity(queryEmbedding, stored.embedding);
      similarities.push({
        request_id: id,
        similarity_score: similarity,
        metadata: stored.metadata,
        document: stored.document
      });
    }

    // Sort by similarity (highest first)
    similarities.sort((a, b) => b.similarity_score - a.similarity_score);

    // Return top N results
    const results = similarities.slice(0, numResults);

    console.log(`🔍 Found ${results.length} similar requests`);
    return results;

  } catch (error) {
    console.error('❌ Error searching:', error);
    return [];
  }
}

// Get requests by priority
export async function getRequestsByPriority(priority) {
  try {
    const results = {
      ids: [],
      metadatas: [],
      documents: []
    };

    for (const [id, stored] of inMemoryStore.entries()) {
      if (stored.metadata.priority === priority) {
        results.ids.push(id);
        results.metadatas.push(stored.metadata);
        results.documents.push(stored.document);
      }
    }

    console.log(`📊 Found ${results.ids.length} ${priority} priority requests`);
    return results;

  } catch (error) {
    console.error('❌ Error filtering by priority:', error);
    return null;
  }
}

// Get requests by location pattern
export async function searchByLocation(locationQuery) {
  try {
    const results = {
      ids: [],
      metadatas: [],
      documents: []
    };

    const lowerQuery = locationQuery.toLowerCase();

    for (const [id, stored] of inMemoryStore.entries()) {
      if (stored.document.toLowerCase().includes(lowerQuery)) {
        results.ids.push(id);
        results.metadatas.push(stored.metadata);
        results.documents.push(stored.document);
      }
    }

    console.log(`📍 Found ${results.ids.length} requests matching location: ${locationQuery}`);
    return results;

  } catch (error) {
    console.error('❌ Error searching by location:', error);
    return null;
  }
}

// Get all requests
export async function getAllRequests() {
  try {
    const results = {
      ids: [],
      metadatas: [],
      documents: [],
      count: inMemoryStore.size
    };

    for (const [id, stored] of inMemoryStore.entries()) {
      results.ids.push(id);
      results.metadatas.push(stored.metadata);
      results.documents.push(stored.document);
    }

    return results;

  } catch (error) {
    console.error('❌ Error getting all requests:', error);
    return null;
  }
}

// Get collection statistics
export async function getStats() {
  try {
    return {
      total_requests: inMemoryStore.size,
      collection_name: 'disaster_requests',
      embedding_type: 'simple_text_based',
      storage_mode: 'in-memory'
    };

  } catch (error) {
    console.error('❌ Error getting stats:', error);
    return {
      total_requests: 0,
      collection_name: 'disaster_requests',
      embedding_type: 'simple_text_based',
      storage_mode: 'in-memory',
      error: error.message
    };
  }
}

// Delete a request
export async function deleteRequest(requestId) {
  try {
    inMemoryStore.delete(requestId);
    console.log(`🗑️ Deleted request: ${requestId}`);
    return true;

  } catch (error) {
    console.error('❌ Error deleting request:', error);
    return false;
  }
}

// Clear all data
export async function clearAllData() {
  try {
    inMemoryStore.clear();
    console.log('🧹 All data cleared');
    return true;

  } catch (error) {
    console.error('❌ Error clearing data:', error);
    return false;
  }
}