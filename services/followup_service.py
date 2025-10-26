"""
Follow-up Service for AgentAid
Handles intelligent follow-up questions and session management
"""

import uuid
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class FollowupService:
    def __init__(self):
        self.active_sessions = {}
        self.session_timeout = 30  # minutes

    def check_completeness(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if extracted data is complete and specific enough"""
        issues = []

        # Check 1: Vague items
        vague_items = ['medicine', 'medical', 'supplies', 'food', 'items', 'stuff', 'things']
        needs_specificity = any(
            any(vague in item.lower() for vague in vague_items)
            for item in extracted_data.get('items', [])
        )

        if needs_specificity:
            issues.append({
                'type': 'vague_items',
                'field': 'items',
                'current_value': extracted_data.get('items', []),
                'question': self._generate_item_specificity_question(extracted_data.get('items', []))
            })

        # Check 2: Missing or vague quantity
        quantity = extracted_data.get('quantity_needed', '')
        if not quantity or quantity.lower() in ['low', 'medium', 'high']:
            issues.append({
                'type': 'vague_quantity',
                'field': 'quantity_needed',
                'current_value': quantity,
                'question': f"Please specify the exact quantity needed for {', '.join(extracted_data.get('items', []))}. For example: '50 units' or '100 bottles'"
            })

        # Check 3: Missing contact information
        if not extracted_data.get('contact'):
            issues.append({
                'type': 'missing_contact',
                'field': 'contact',
                'current_value': None,
                'question': 'Please provide a contact phone number so we can coordinate the delivery.'
            })

        # Check 4: Vague location
        location = extracted_data.get('location', '')
        if not location or len(location) < 10 or not self._has_specific_address(location):
            issues.append({
                'type': 'vague_location',
                'field': 'location',
                'current_value': location,
                'question': 'Please provide a specific address or landmark. For example: "123 Main Street" or "Lincoln High School, Room 101"'
            })

        completeness_score = self._calculate_completeness_score(extracted_data, issues)

        return {
            'is_complete': len(issues) == 0,
            'issues': issues,
            'completeness_score': completeness_score,
            'needs_followup': len(issues) > 0
        }

    def _generate_item_specificity_question(self, items: List[str]) -> str:
        """Generate specific questions for vague items"""
        questions = []

        for item in items:
            lower = item.lower()

            if 'medicine' in lower or 'medical' in lower:
                questions.append('What specific medicine or medical supplies do you need? (e.g., bandages, pain medication, insulin, antibiotics)')
            elif 'food' in lower:
                questions.append('What specific food items do you need? (e.g., baby formula, canned goods, rice, protein bars)')
            elif 'supplies' in lower:
                questions.append('What specific supplies do you need? Please list the exact items.')

        return ' '.join(questions) if questions else 'Please specify exactly what items you need.'

    def _has_specific_address(self, location: str) -> bool:
        """Check if location is specific enough"""
        import re
        specific_indicators = [
            r'\d+\s+\w+\s+(street|st|avenue|ave|road|rd|blvd|drive|dr|lane|ln)',
            r'room\s+\d+',
            r'building\s+\w+',
            r'\d+\s+\w+',  # Any number followed by text
        ]

        return any(re.search(pattern, location, re.IGNORECASE) for pattern in specific_indicators)

    def _calculate_completeness_score(self, data: Dict[str, Any], issues: List[Dict[str, Any]]) -> int:
        """Calculate completeness score (0-100)"""
        total_fields = 5  # items, quantity, location, contact, priority
        missing_fields = len(issues)
        return max(0, round(((total_fields - missing_fields) / total_fields) * 100))

    def generate_followup_questions(self, extracted_data: Dict[str, Any], user_input: str) -> Optional[Dict[str, Any]]:
        """Generate follow-up questions using AI"""
        completeness_check = self.check_completeness(extracted_data)

        if completeness_check['is_complete']:
            return None

        # Generate contextual follow-up message
        followup_message = self._generate_contextual_followup(extracted_data, user_input, completeness_check['issues'])

        return {
            'needs_followup': True,
            'completeness_score': completeness_check['completeness_score'],
            'issues': completeness_check['issues'],
            'followup_message': followup_message,
            'session_id': self._generate_session_id()
        }

    def _generate_contextual_followup(self, extracted_data: Dict[str, Any], user_input: str, issues: List[Dict[str, Any]]) -> str:
        """Generate contextual follow-up message"""
        if not issues:
            return ""

        # Simple rule-based follow-up generation
        messages = []

        for issue in issues:
            if issue['type'] == 'vague_items':
                messages.append("Please specify exactly what items you need. For example: 'bandages and pain medication' instead of 'medical supplies'.")
            elif issue['type'] == 'vague_quantity':
                messages.append("Please provide specific quantities. For example: '50 units' or '100 bottles'.")
            elif issue['type'] == 'missing_contact':
                messages.append("Please provide a contact phone number so we can coordinate delivery.")
            elif issue['type'] == 'vague_location':
                messages.append("Please provide a specific address or landmark where you need help.")

        return " ".join(messages)

    def merge_followup_response(self, original_data: Dict[str, Any], followup_input: str, session_id: str) -> Dict[str, Any]:
        """Merge follow-up response with original data"""
        # Simple merge strategy - append to additional_notes
        merged_data = original_data.copy()

        current_notes = merged_data.get('additional_notes', '')
        if current_notes:
            merged_data['additional_notes'] = f"{current_notes}\nFollow-up: {followup_input}"
        else:
            merged_data['additional_notes'] = f"Follow-up: {followup_input}"

        merged_data.update({
            'timestamp': datetime.now().isoformat(),
            'follow_up_completed': True
        })

        return merged_data

    def store_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """Store session data"""
        self.active_sessions[session_id] = {
            **data,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=self.session_timeout)).isoformat()
        }

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None

        # Check if expired
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            del self.active_sessions[session_id]
            return None

        return session

    def delete_session(self, session_id: str) -> None:
        """Delete session"""
        self.active_sessions.pop(session_id, None)

    def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        now = datetime.now()
        expired_sessions = []

        for session_id, session in self.active_sessions.items():
            expires_at = datetime.fromisoformat(session['expires_at'])
            if now > expires_at:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.active_sessions[session_id]

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"SESSION-{int(datetime.now().timestamp())}-{uuid.uuid4().hex[:8]}"
