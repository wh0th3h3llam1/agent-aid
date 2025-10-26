"""
Vector Database Service for AgentAid
Simple in-memory vector database for request storage and similarity search
"""

import json
import math
import numpy as np
from typing import Dict, List, Any, Optional
from collections import defaultdict

class VectorDatabase:
    def __init__(self):
        self.requests = {}  # request_id -> request_data
        self.embeddings = {}  # request_id -> embedding vector
        self.metadata = {}  # request_id -> metadata

    def store_request(self, request_data: Dict[str, Any]) -> bool:
        """Store a disaster request with embedding"""
        try:
            request_id = request_data.get('request_id')
            if not request_id:
                return False

            # Create searchable text
            searchable_text = self._create_searchable_text(request_data)

            # Generate embedding
            embedding = self._generate_embedding(searchable_text)

            # Store data
            self.requests[request_id] = request_data
            self.embeddings[request_id] = embedding
            self.metadata[request_id] = {
                'request_id': request_id,
                'priority': request_data.get('priority', 'unknown'),
                'location': request_data.get('location', ''),
                'items': json.dumps(request_data.get('items', [])),
                'victim_count': request_data.get('victim_count', 0),
                'timestamp': request_data.get('timestamp', ''),
                'searchable_text': searchable_text
            }

            print(f"📊 Stored request: {request_id}")
            return True

        except Exception as e:
            print(f"❌ Error storing request: {e}")
            return False

    def _create_searchable_text(self, request_data: Dict[str, Any]) -> str:
        """Create searchable text from request data"""
        parts = []

        if request_data.get('items'):
            parts.append(f"Items: {', '.join(request_data['items'])}")

        if request_data.get('location'):
            parts.append(f"Location: {request_data['location']}")

        if request_data.get('priority'):
            parts.append(f"Priority: {request_data['priority']}")

        if request_data.get('additional_notes'):
            parts.append(f"Notes: {request_data['additional_notes']}")

        if request_data.get('victim_count'):
            parts.append(f"Victim Count: {request_data['victim_count']}")

        if request_data.get('raw_input'):
            parts.append(f"Raw Input: {request_data['raw_input']}")

        return " ".join(parts)

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate simple text-based embedding"""
        # Simple word-based embedding (384 dimensions)
        words = text.lower().split()
        embedding = [0.0] * 384

        for word in words:
            # Simple hash-based embedding
            word_hash = hash(word) % 384
            embedding[word_hash] += 1.0

        # Normalize
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    def find_similar_requests(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar requests using cosine similarity"""
        try:
            if not self.embeddings:
                return []

            # Generate query embedding
            query_embedding = self._generate_embedding(query_text)

            # Calculate similarities
            similarities = []

            for request_id, embedding in self.embeddings.items():
                similarity = self._cosine_similarity(query_embedding, embedding)
                similarities.append({
                    'request_id': request_id,
                    'similarity_score': similarity,
                    'metadata': self.metadata.get(request_id, {}),
                    'document': self.metadata.get(request_id, {}).get('searchable_text', '')
                })

            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)

            # Return top results
            return similarities[:limit]

        except Exception as e:
            print(f"❌ Error finding similar requests: {e}")
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def get_requests_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get requests filtered by priority"""
        results = []

        for request_id, meta in self.metadata.items():
            if meta.get('priority') == priority:
                results.append({
                    'request_id': request_id,
                    'metadata': meta,
                    'request_data': self.requests.get(request_id, {})
                })

        return results

    def search_by_location(self, location_query: str) -> List[Dict[str, Any]]:
        """Search requests by location"""
        results = []
        location_lower = location_query.lower()

        for request_id, meta in self.metadata.items():
            if location_lower in meta.get('location', '').lower():
                results.append({
                    'request_id': request_id,
                    'metadata': meta,
                    'request_data': self.requests.get(request_id, {})
                })

        return results

    def get_all_requests(self) -> List[Dict[str, Any]]:
        """Get all stored requests"""
        results = []

        for request_id in self.requests.keys():
            results.append({
                'request_id': request_id,
                'metadata': self.metadata.get(request_id, {}),
                'request_data': self.requests.get(request_id, {})
            })

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        total_requests = len(self.requests)

        # Count by priority
        priority_counts = defaultdict(int)
        for meta in self.metadata.values():
            priority_counts[meta.get('priority', 'unknown')] += 1

        return {
            'total_requests': total_requests,
            'by_priority': dict(priority_counts),
            'storage_mode': 'in-memory',
            'embedding_type': 'simple_text_based'
        }

    def delete_request(self, request_id: str) -> bool:
        """Delete a request"""
        try:
            self.requests.pop(request_id, None)
            self.embeddings.pop(request_id, None)
            self.metadata.pop(request_id, None)
            print(f"🗑️ Deleted request: {request_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting request: {e}")
            return False

    def clear_all_data(self) -> bool:
        """Clear all stored data"""
        try:
            self.requests.clear()
            self.embeddings.clear()
            self.metadata.clear()
            print("🧹 All data cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
            return False
