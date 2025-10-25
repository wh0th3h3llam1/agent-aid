import Anthropic from '@anthropic-ai/sdk';
import dotenv from 'dotenv';
import { geocodeAddress } from './geocodingService.js';

dotenv.config();

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const EXTRACTION_PROMPT = `You are a disaster response AI assistant. Extract structured information from victim reports.

Extract the following fields:
- items: array of needed items (food, water, medical supplies, shelter, etc.)
- quantity_needed: specific numbers or "low", "medium", "high"
- location: DETAILED address or description of location (be as specific as possible)
- priority: "low", "medium", "high", "critical" (based on urgency indicators)
- contact: phone number or contact info if provided
- additional_notes: any other relevant details
- victim_count: estimated number of people affected (if mentioned)

IMPORTANT: For location, extract the most specific address possible. Look for:
- Street addresses (123 Main Street)
- Building names (Lincoln High School, County Hospital)
- Room numbers (Room 101, Building A)
- Landmarks (near the old church, by the river)
- Intersections (corner of 5th and Main)

Return ONLY valid JSON with these fields. If information is missing, use null.`;

export async function extractDisasterData(rawInput) {
  try {
    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-5-20250929',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: `${EXTRACTION_PROMPT}\n\nVictim Report: "${rawInput}"`
        }
      ]
    });

    const extractedText = message.content[0].text;
    
    // Parse JSON from Claude's response
    const jsonMatch = extractedText.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('No valid JSON found in response');
    }

    const structuredData = JSON.parse(jsonMatch[0]);
    
    // 🌍 GEOCODE THE LOCATION
    let geocoded = null;
    if (structuredData.location) {
      geocoded = await geocodeAddress(structuredData.location);
    }
    
    // Add metadata with geocoding
    return {
      ...structuredData,
      coordinates: geocoded ? {
        latitude: geocoded.latitude,
        longitude: geocoded.longitude,
        formatted_address: geocoded.formatted_address,
        confidence: geocoded.confidence,
        city: geocoded.components.city,
        state: geocoded.components.state,
        country: geocoded.components.country
      } : null,
      timestamp: new Date().toISOString(),
      raw_input: rawInput,
      request_id: generateRequestId()
    };

  } catch (error) {
    console.error('Claude extraction error:', error);
    throw error;
  }
}

function generateRequestId() {
  return `REQ-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}