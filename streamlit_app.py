#!/usr/bin/env python3
"""
AgentAid Streamlit Application
Python-based disaster response coordination platform
"""

import streamlit as st
import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
from pathlib import Path

# Import our services
try:
    from services.claude_service import ClaudeService
    from services.geocoding_service import GeocodingService
    from services.followup_service import FollowupService
    from services.vector_db import VectorDatabase
    from services.agent_integration import AgentIntegration
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AgentAid - Disaster Response",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AgentAidApp:
    def __init__(self):
        try:
            self.claude_service = ClaudeService()
            self.geocoding_service = GeocodingService()
            self.followup_service = FollowupService()
            self.vector_db = VectorDatabase()
            self.agent_integration = AgentIntegration()
        except Exception as e:
            st.error(f"Failed to initialize services: {e}")
            st.stop()

        # Initialize session state
        if 'requests' not in st.session_state:
            st.session_state.requests = []
        if 'current_session_id' not in st.session_state:
            st.session_state.current_session_id = None
        if 'followup_needed' not in st.session_state:
            st.session_state.followup_needed = False

    def render_header(self):
        """Render the main header"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #1e3c72; font-size: 3rem; margin-bottom: 1rem;">🚨 AgentAid</h1>
            <p style="font-size: 1.2rem; color: #666;">AI-Powered Disaster Response Coordination Platform</p>
        </div>
        """, unsafe_allow_html=True)

    def render_disaster_form(self):
        """Render the disaster request form"""
        st.markdown("## 📝 Report Disaster Need")

        with st.form("disaster_form", clear_on_submit=False):
            col1, col2 = st.columns(2)

            with col1:
                items = st.text_area(
                    "What do you need? *",
                    placeholder="e.g., 50 blankets, 100 water bottles, medical supplies",
                    help="Describe the items you need in detail"
                )

                quantity = st.text_input(
                    "Quantity Details",
                    placeholder="e.g., 50 units, 100 bottles, 10 boxes",
                    help="Specify exact quantities if known"
                )

                location = st.text_input(
                    "Location *",
                    placeholder="e.g., 123 Main St, Berkeley, CA",
                    help="Provide specific address or landmark"
                )

            with col2:
                contact = st.text_input(
                    "Contact Information",
                    placeholder="Phone number or email",
                    help="How can we reach you?"
                )

                victim_count = st.number_input(
                    "Number of People Affected",
                    min_value=1,
                    value=1,
                    help="Estimated number of people affected"
                )

                priority = st.selectbox(
                    "Priority Level *",
                    ["medium", "low", "high", "critical"],
                    index=0,
                    help="How urgent is this request?"
                )

            submitted = st.form_submit_button("🚀 Submit Request", use_container_width=True)

            if submitted:
                if not items or not location:
                    st.error("Please fill in the required fields: Items and Location")
                else:
                    self.process_disaster_request({
                        'items': items,
                        'quantity': quantity,
                        'location': location,
                        'contact': contact,
                        'victim_count': victim_count,
                        'priority': priority
                    })

    def process_disaster_request(self, form_data: Dict[str, Any]):
        """Process a disaster request through the AI pipeline"""
        with st.spinner("🤖 Processing your request with AI..."):
            try:
                # Create natural language input
                natural_input = self.create_natural_language_input(form_data)

                # Extract structured data using Claude
                structured_data = self.claude_service.extract_disaster_data(natural_input)

                # Check if follow-up is needed
                followup_check = self.followup_service.check_completeness(structured_data)

                if followup_check and followup_check.get('needs_followup'):
                    # Store session for follow-up
                    session_id = str(uuid.uuid4())
                    st.session_state.current_session_id = session_id
                    st.session_state.followup_needed = True

                    self.followup_service.store_session(session_id, {
                        'original_data': structured_data,
                        'original_input': natural_input
                    })

                    st.warning("⚠️ Additional Information Needed")
                    st.info(f"**Completeness:** {followup_check['completeness_score']}%")
                    st.markdown(f"**Please provide:**\n{followup_check['followup_message']}")

                    # Show follow-up form
                    self.render_followup_form(session_id)

                else:
                    # Process complete request
                    self.process_complete_request(structured_data)

            except Exception as e:
                st.error(f"Error processing request: {str(e)}")
                st.exception(e)

    def render_followup_form(self, session_id: str):
        """Render follow-up form for incomplete requests"""
        st.markdown("### 📝 Additional Information")

        with st.form("followup_form"):
            followup_input = st.text_area(
                "Please provide the additional information:",
                placeholder="Answer the questions above...",
                height=100
            )

            submitted = st.form_submit_button("✅ Submit Additional Information")

            if submitted and followup_input:
                self.process_followup_response(session_id, followup_input)

    def process_followup_response(self, session_id: str, followup_input: str):
        """Process follow-up response and merge with original data"""
        with st.spinner("🔄 Processing additional information..."):
            try:
                # Get original session data
                session_data = self.followup_service.get_session(session_id)
                if not session_data:
                    st.error("Session expired. Please start over.")
                    return

                # Merge follow-up with original data
                merged_data = self.followup_service.merge_followup_response(
                    session_data['original_data'],
                    followup_input,
                    session_id
                )

                # Clean up session
                self.followup_service.delete_session(session_id)
                st.session_state.current_session_id = None
                st.session_state.followup_needed = False

                # Process complete request
                self.process_complete_request(merged_data)

            except Exception as e:
                st.error(f"Error processing follow-up: {str(e)}")

    def process_complete_request(self, structured_data: Dict[str, Any]):
        """Process a complete disaster request"""
        try:
            # Geocode the location
            if structured_data.get('location'):
                coordinates = self.geocoding_service.geocode_address(structured_data['location'])
                if coordinates:
                    structured_data['coordinates'] = coordinates

            # Store in vector database
            self.vector_db.store_request(structured_data)

            # Add to session state
            st.session_state.requests.append(structured_data)

            # Send to agent system
            self.agent_integration.send_to_agents(structured_data)

            # Show success message
            st.success("✅ Request Processed Successfully!")
            st.markdown(f"**Request ID:** {structured_data.get('request_id', 'N/A')}")
            st.markdown(f"**Priority:** {structured_data.get('priority', 'N/A').upper()}")
            st.markdown(f"**Items:** {', '.join(structured_data.get('items', []))}")
            st.markdown(f"**Location:** {structured_data.get('location', 'N/A')}")

            if structured_data.get('coordinates'):
                st.markdown(f"**Coordinates:** {structured_data['coordinates']['latitude']:.4f}, {structured_data['coordinates']['longitude']:.4f}")

            st.markdown(f"**Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            st.error(f"Error processing complete request: {str(e)}")

    def create_natural_language_input(self, form_data: Dict[str, Any]) -> str:
        """Convert form data to natural language"""
        input_text = f"We need {form_data['items']}"

        if form_data.get('quantity'):
            input_text += f" ({form_data['quantity']})"

        input_text += f" at {form_data['location']}"

        if form_data.get('victim_count'):
            input_text += f". There are approximately {form_data['victim_count']} people affected"

        if form_data.get('contact'):
            input_text += f". Contact: {form_data['contact']}"

        input_text += f". This is a {form_data['priority']} priority request."

        return input_text

    def render_system_status(self):
        """Render system status sidebar"""
        st.sidebar.markdown("## 🤖 System Status")

        # Check Claude service
        try:
            claude_status = self.claude_service.check_health()
            if claude_status:
                st.sidebar.success("✅ Claude Service: Active")
            else:
                st.sidebar.error("❌ Claude Service: Offline")
        except:
            st.sidebar.error("❌ Claude Service: Error")

        # Check geocoding service
        try:
            geocoding_status = self.geocoding_service.check_health()
            if geocoding_status:
                st.sidebar.success("✅ Geocoding Service: Active")
            else:
                st.sidebar.warning("⚠️ Geocoding Service: Limited")
        except:
            st.sidebar.warning("⚠️ Geocoding Service: Error")

        # Show request statistics
        total_requests = len(st.session_state.requests)
        st.sidebar.metric("Total Requests", total_requests)

        if total_requests > 0:
            priorities = {}
            for req in st.session_state.requests:
                priority = req.get('priority', 'unknown')
                priorities[priority] = priorities.get(priority, 0) + 1

            for priority, count in priorities.items():
                st.sidebar.metric(f"{priority.title()} Priority", count)

    def render_recent_requests(self):
        """Render recent requests section"""
        if not st.session_state.requests:
            st.markdown("## 📋 Recent Requests")
            st.info("No requests submitted yet. Fill out the form above to get started.")
            return

        st.markdown("## 📋 Recent Requests")

        for i, request in enumerate(st.session_state.requests[-5:]):  # Show last 5
            with st.expander(f"Request {i+1}: {request.get('request_id', 'N/A')} - {request.get('priority', 'N/A').upper()}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Items:** {', '.join(request.get('items', []))}")
                    st.markdown(f"**Location:** {request.get('location', 'N/A')}")
                    st.markdown(f"**Contact:** {request.get('contact', 'Not provided')}")

                with col2:
                    st.markdown(f"**Priority:** {request.get('priority', 'N/A').upper()}")
                    st.markdown(f"**Victim Count:** {request.get('victim_count', 'Unknown')}")
                    if request.get('coordinates'):
                        st.markdown(f"**Coordinates:** {request['coordinates']['latitude']:.4f}, {request['coordinates']['longitude']:.4f}")

                st.markdown("**Status:** 🤖 Being processed by AI coordination agents...")

    def render_similar_requests(self):
        """Render similar requests section"""
        if len(st.session_state.requests) < 2:
            return

        st.markdown("## 🔍 Similar Requests")

        # Get the most recent request for similarity search
        latest_request = st.session_state.requests[-1]
        search_text = f"{' '.join(latest_request.get('items', []))} {latest_request.get('location', '')}"

        try:
            similar_requests = self.vector_db.find_similar_requests(search_text, limit=3)

            if similar_requests:
                for i, similar in enumerate(similar_requests):
                    if similar['request_id'] != latest_request.get('request_id'):
                        st.markdown(f"**Similar Request {i+1}:** {similar['similarity_score']:.2f} similarity")
                        st.markdown(f"- Items: {similar['metadata'].get('items', 'N/A')}")
                        st.markdown(f"- Location: {similar['metadata'].get('location', 'N/A')}")
                        st.markdown(f"- Priority: {similar['metadata'].get('priority', 'N/A')}")
                        st.markdown("---")
        except Exception as e:
            st.warning(f"Could not find similar requests: {str(e)}")

    def run(self):
        """Main application runner"""
        self.render_header()

        # Create main layout
        col1, col2 = st.columns([2, 1])

        with col1:
            if not st.session_state.followup_needed:
                self.render_disaster_form()
            else:
                st.info("Please complete the follow-up form above.")

            self.render_recent_requests()
            self.render_similar_requests()

        with col2:
            self.render_system_status()

def main():
    """Main entry point"""
    app = AgentAidApp()
    app.run()

if __name__ == "__main__":
    main()
