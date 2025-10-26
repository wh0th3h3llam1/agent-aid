"""
Agent Integration Service for AgentAid
Handles communication with existing uAgent system
"""

import requests
import json
from typing import Dict, List, Any, Optional
import time

class AgentIntegration:
    def __init__(self):
        self.claude_service_url = "http://localhost:3000"
        self.timeout = 10

    def send_to_agents(self, request_data: Dict[str, Any]) -> bool:
        """Send request to the agent coordination system"""
        try:
            # Format request for uAgent system
            agent_payload = self._format_for_uagent(request_data)

            # Send to Claude service for agent processing
            response = requests.post(
                f"{self.claude_service_url}/api/uagent/update",
                json={
                    "request_id": request_data.get('request_id'),
                    "agent_id": "streamlit_app",
                    "status": "pending",
                    "data": agent_payload
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                print(f"✅ Request sent to agents: {request_data.get('request_id')}")
                return True
            else:
                print(f"⚠️ Failed to send to agents: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending to agents: {e}")
            return False

    def _format_for_uagent(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format request data for uAgent system"""
        return {
            "request_id": request_data.get('request_id'),
            "items": request_data.get('items', []),
            "quantity": request_data.get('quantity_needed', ''),
            "location": {
                "address": request_data.get('location', ''),
                "coordinates": request_data.get('coordinates')
            },
            "priority": request_data.get('priority', 'medium'),
            "urgency_level": self._get_urgency_level(request_data.get('priority', 'medium')),
            "status": "pending",
            "geocoded": bool(request_data.get('coordinates')),
            "victim_count": request_data.get('victim_count', 0),
            "contact": request_data.get('contact', ''),
            "timestamp": request_data.get('timestamp', ''),
            "raw_input": request_data.get('raw_input', '')
        }

    def _get_urgency_level(self, priority: str) -> int:
        """Convert priority to urgency level (1-4)"""
        priority_map = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return priority_map.get(priority.lower(), 2)

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get pending requests from agent system"""
        try:
            response = requests.get(
                f"{self.claude_service_url}/api/uagent/pending-requests",
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('requests', [])
            else:
                print(f"⚠️ Failed to get pending requests: {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting pending requests: {e}")
            return []

    def get_nearby_requests(self, latitude: float, longitude: float, radius_km: float = 50) -> List[Dict[str, Any]]:
        """Get requests near a location"""
        try:
            response = requests.post(
                f"{self.claude_service_url}/api/uagent/requests-nearby",
                json={
                    "latitude": latitude,
                    "longitude": longitude,
                    "radius_km": radius_km
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('requests', [])
            else:
                print(f"⚠️ Failed to get nearby requests: {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting nearby requests: {e}")
            return []

    def claim_request(self, request_id: str, agent_id: str) -> bool:
        """Claim a request for processing"""
        try:
            response = requests.post(
                f"{self.claude_service_url}/api/uagent/claim-request",
                json={
                    "request_id": request_id,
                    "agent_id": agent_id,
                    "agent_address": f"agent_{agent_id}"
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                print(f"✅ Request claimed: {request_id}")
                return True
            else:
                print(f"⚠️ Failed to claim request: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Error claiming request: {e}")
            return False

    def update_request_status(self, request_id: str, status: str, additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update request status"""
        try:
            update_data = {
                "request_id": request_id,
                "agent_id": "streamlit_app",
                "status": status
            }

            if additional_data:
                update_data.update(additional_data)

            response = requests.post(
                f"{self.claude_service_url}/api/uagent/update",
                json=update_data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                print(f"✅ Status updated: {request_id} -> {status}")
                return True
            else:
                print(f"⚠️ Failed to update status: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Error updating status: {e}")
            return False

    def get_agent_updates(self) -> List[Dict[str, Any]]:
        """Get agent updates"""
        try:
            response = requests.get(
                f"{self.claude_service_url}/api/uagent/updates",
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('updates', [])
            else:
                print(f"⚠️ Failed to get agent updates: {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting agent updates: {e}")
            return []

    def check_health(self) -> bool:
        """Check if agent system is healthy"""
        try:
            response = requests.get(
                f"{self.claude_service_url}/health",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'ok'
            else:
                return False

        except requests.exceptions.RequestException:
            return False

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            response = requests.get(
                f"{self.claude_service_url}/api/stats",
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('stats', {})
            else:
                return {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting system stats: {e}")
            return {}
