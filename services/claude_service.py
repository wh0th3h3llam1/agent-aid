"""
Claude AI Service for AgentAid
Handles disaster data extraction using Claude AI
"""

import os
import json
import uuid
from typing import Dict, Any, Optional
import anthropic
from datetime import datetime

class ClaudeService:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.client = anthropic.Anthropic(api_key=self.api_key)

        self.extraction_prompt = """You are a disaster response AI assistant. Extract structured information from victim reports.

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

Return ONLY valid JSON with these fields. If information is missing, use null."""

    def extract_disaster_data(self, raw_input: str) -> Dict[str, Any]:
        """Extract structured disaster data from natural language input"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"{self.extraction_prompt}\n\nVictim Report: \"{raw_input}\""
                    }
                ]
            )

            extracted_text = response.content[0].text

            # Parse JSON from Claude's response
            json_match = self._extract_json_from_text(extracted_text)
            if not json_match:
                raise ValueError("No valid JSON found in Claude response")

            structured_data = json.loads(json_match)

            # Add metadata
            structured_data.update({
                'timestamp': datetime.now().isoformat(),
                'raw_input': raw_input,
                'request_id': self._generate_request_id()
            })

            return structured_data

        except Exception as e:
            print(f"Claude extraction error: {e}")
            raise e

    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """Extract JSON from Claude's response text"""
        import re
        json_match = re.search(r'\{[\s\S]*\}', text)
        return json_match.group(0) if json_match else None

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"REQ-{int(datetime.now().timestamp())}-{uuid.uuid4().hex[:8]}"

    def check_health(self) -> bool:
        """Check if Claude service is healthy"""
        try:
            # Simple test message
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return response is not None
        except Exception:
            return False

    def generate_followup_questions(self, extracted_data: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Generate follow-up questions for incomplete data"""
        followup_prompt = f"""You are a disaster response assistant collecting information.

Original request: "{user_input}"

Extracted data so far:
{json.dumps(extracted_data, indent=2)}

Generate a helpful, empathetic follow-up message that asks for missing information. Be:
1. Compassionate (they're in a disaster situation)
2. Clear and specific
3. Brief (ask all questions in one message)
4. Practical

Return ONLY the follow-up message text, nothing else."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[{"role": "user", "content": followup_prompt}]
            )

            return {
                'followup_message': response.content[0].text,
                'needs_followup': True
            }
        except Exception as e:
            print(f"Error generating follow-up: {e}")
            return {
                'followup_message': "Please provide more specific information about your needs.",
                'needs_followup': True
            }

    def merge_followup_response(self, original_data: Dict[str, Any], followup_input: str) -> Dict[str, Any]:
        """Merge follow-up response with original data"""
        merge_prompt = f"""You are merging follow-up information with an existing disaster request.

Original extracted data:
{json.dumps(original_data, indent=2)}

Follow-up response from user:
"{followup_input}"

Update the original data with the new information. Return ONLY valid JSON with the complete, merged data structure. Keep all original fields and update/add based on the follow-up response."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": merge_prompt}]
            )

            merged_text = response.content[0].text
            json_match = self._extract_json_from_text(merged_text)

            if not json_match:
                raise ValueError("No valid JSON found in merge response")

            merged_data = json.loads(json_match)

            # Preserve original metadata
            merged_data.update({
                'timestamp': datetime.now().isoformat(),
                'request_id': original_data.get('request_id'),
                'raw_input': f"{original_data.get('raw_input', '')}\n[Follow-up]: {followup_input}",
                'follow_up_completed': True
            })

            return merged_data

        except Exception as e:
            print(f"Error merging follow-up: {e}")
            # Fallback: simple merge
            return {
                **original_data,
                'additional_notes': f"{original_data.get('additional_notes', '')}\nFollow-up: {followup_input}".strip(),
                'timestamp': datetime.now().isoformat(),
                'follow_up_completed': True
            }
