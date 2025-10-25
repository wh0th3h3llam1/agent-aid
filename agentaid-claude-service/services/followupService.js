import Anthropic from '@anthropic-ai/sdk';
import dotenv from 'dotenv';

dotenv.config();

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Check if information is complete and specific enough
export function checkCompleteness(extractedData) {
  const issues = [];
  
  // Check 1: Vague items (medicine, food, supplies)
  const vagueItems = ['medicine', 'medical', 'supplies', 'food', 'items', 'stuff', 'things'];
  const needsSpecificity = extractedData.items.some(item => 
    vagueItems.some(vague => item.toLowerCase().includes(vague))
  );
  
  if (needsSpecificity) {
    issues.push({
      type: 'vague_items',
      field: 'items',
      current_value: extractedData.items,
      question: generateItemSpecificityQuestion(extractedData.items)
    });
  }
  
  // Check 2: Missing or vague quantity
  if (!extractedData.quantity_needed || 
      (typeof extractedData.quantity_needed === 'string' && 
       ['low', 'medium', 'high'].includes(extractedData.quantity_needed.toLowerCase()))) {
    issues.push({
      type: 'vague_quantity',
      field: 'quantity_needed',
      current_value: extractedData.quantity_needed,
      question: `Please specify the exact quantity needed for ${extractedData.items.join(', ')}. For example: "50 units" or "100 bottles"`
    });
  }
  
  // Check 3: Missing contact information
  if (!extractedData.contact) {
    issues.push({
      type: 'missing_contact',
      field: 'contact',
      current_value: null,
      question: 'Please provide a contact phone number so we can coordinate the delivery.'
    });
  }
  
  // Check 4: Vague location
  if (!extractedData.location || 
      extractedData.location.length < 10 || 
      !hasSpecificAddress(extractedData.location)) {
    issues.push({
      type: 'vague_location',
      field: 'location',
      current_value: extractedData.location,
      question: 'Please provide a specific address or landmark. For example: "123 Main Street" or "Lincoln High School, Room 101"'
    });
  }
  
  return {
    is_complete: issues.length === 0,
    issues: issues,
    completeness_score: calculateCompletenessScore(extractedData, issues)
  };
}

// Generate specific questions for vague items
function generateItemSpecificityQuestion(items) {
  const itemQuestions = items.map(item => {
    const lower = item.toLowerCase();
    
    if (lower.includes('medicine') || lower.includes('medical')) {
      return 'What specific medicine or medical supplies do you need? (e.g., bandages, pain medication, insulin, antibiotics)';
    }
    
    if (lower.includes('food')) {
      return 'What specific food items do you need? (e.g., baby formula, canned goods, rice, protein bars)';
    }
    
    if (lower.includes('supplies')) {
      return 'What specific supplies do you need? Please list the exact items.';
    }
    
    return null;
  }).filter(q => q !== null);
  
  return itemQuestions.length > 0 
    ? itemQuestions.join(' ') 
    : 'Please specify exactly what items you need.';
}

// Check if location is specific enough
function hasSpecificAddress(location) {
  const specificIndicators = [
    /\d+\s+\w+\s+(street|st|avenue|ave|road|rd|blvd|drive|dr|lane|ln)/i,
    /room\s+\d+/i,
    /building\s+\w+/i,
    /\d+\s+\w+/,  // Any number followed by text (likely address)
  ];
  
  return specificIndicators.some(pattern => pattern.test(location));
}

// Calculate completeness score (0-100)
function calculateCompletenessScore(data, issues) {
  const totalFields = 5; // items, quantity, location, contact, priority
  const missingFields = issues.length;
  return Math.round(((totalFields - missingFields) / totalFields) * 100);
}

// Use Claude to generate contextual follow-up questions
export async function generateFollowupQuestions(extractedData, userInput) {
  const completenessCheck = checkCompleteness(extractedData);
  
  if (completenessCheck.is_complete) {
    return null; // No follow-up needed
  }
  
  const FOLLOWUP_PROMPT = `You are a disaster response assistant collecting information. 

Original request: "${userInput}"

Extracted data so far:
${JSON.stringify(extractedData, null, 2)}

Issues identified:
${JSON.stringify(completenessCheck.issues, null, 2)}

Generate a helpful, empathetic follow-up message that asks for the missing information. Be:
1. Compassionate (they're in a disaster situation)
2. Clear and specific
3. Brief (ask all questions in one message)
4. Practical

Return ONLY the follow-up message text, nothing else.`;

  try {
    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-5-20250929',
      max_tokens: 512,
      messages: [
        {
          role: 'user',
          content: FOLLOWUP_PROMPT
        }
      ]
    });

    return {
      needs_followup: true,
      completeness_score: completenessCheck.completeness_score,
      issues: completenessCheck.issues,
      followup_message: message.content[0].text,
      session_id: generateSessionId()
    };

  } catch (error) {
    console.error('Error generating follow-up:', error);
    // Fallback to simple concatenated questions
    return {
      needs_followup: true,
      completeness_score: completenessCheck.completeness_score,
      issues: completenessCheck.issues,
      followup_message: completenessCheck.issues.map(i => i.question).join('\n\n'),
      session_id: generateSessionId()
    };
  }
}

// Merge follow-up responses with original data
export async function mergeFollowupResponse(originalData, followupInput, sessionId) {
  const MERGE_PROMPT = `You are merging follow-up information with an existing disaster request.

Original extracted data:
${JSON.stringify(originalData, null, 2)}

Follow-up response from user:
"${followupInput}"

Update the original data with the new information. Return ONLY valid JSON with the complete, merged data structure. Keep all original fields and update/add based on the follow-up response.`;

  try {
    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-5-20250929',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: MERGE_PROMPT
        }
      ]
    });

    const extractedText = message.content[0].text;
    const jsonMatch = extractedText.match(/\{[\s\S]*\}/);
    
    if (!jsonMatch) {
      throw new Error('No valid JSON found in merge response');
    }

    const mergedData = JSON.parse(jsonMatch[0]);
    
    return {
      ...mergedData,
      timestamp: new Date().toISOString(),
      request_id: originalData.request_id,
      raw_input: `${originalData.raw_input}\n[Follow-up]: ${followupInput}`,
      follow_up_completed: true
    };

  } catch (error) {
    console.error('Error merging follow-up:', error);
    throw error;
  }
}

// Generate session ID for tracking multi-turn conversations
function generateSessionId() {
  return `SESSION-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Store for active follow-up sessions
const activeSessions = new Map();

export function storeSession(sessionId, data) {
  activeSessions.set(sessionId, {
    ...data,
    created_at: new Date().toISOString(),
    expires_at: new Date(Date.now() + 30 * 60 * 1000).toISOString() // 30 min expiry
  });
}

export function getSession(sessionId) {
  return activeSessions.get(sessionId);
}

export function deleteSession(sessionId) {
  activeSessions.delete(sessionId);
}

export function cleanupExpiredSessions() {
  const now = Date.now();
  for (const [sessionId, session] of activeSessions.entries()) {
    if (new Date(session.expires_at).getTime() < now) {
      activeSessions.delete(sessionId);
    }
  }
}

// Run cleanup every 5 minutes
setInterval(cleanupExpiredSessions, 5 * 60 * 1000);