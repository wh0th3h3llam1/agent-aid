"""
Geocoding Service for AgentAid
Handles address geocoding using OpenStreetMap Nominatim
"""

import requests
import time
from typing import Dict, Any, Optional, List
import math

class GeocodingService:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'AgentAid-DisasterResponse/1.0'  # Required by Nominatim
        }
        self.rate_limit_delay = 1.0  # Seconds between requests

    def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocode an address to coordinates"""
        if not address or len(address.strip()) < 5:
            print("⚠️ Address too short for geocoding")
            return None

        print(f"🌍 Geocoding address: \"{address}\"")

        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }

            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if data and len(data) > 0:
                    result = data[0]

                    geocoded = {
                        'latitude': float(result['lat']),
                        'longitude': float(result['lon']),
                        'formatted_address': result['display_name'],
                        'confidence': 0.8,  # Nominatim doesn't provide confidence
                        'components': {
                            'city': result.get('address', {}).get('city') or result.get('address', {}).get('town'),
                            'state': result.get('address', {}).get('state'),
                            'country': result.get('address', {}).get('country'),
                            'postcode': result.get('address', {}).get('postcode')
                        }
                    }

                    print(f"✅ Geocoded: {geocoded['latitude']}, {geocoded['longitude']}")
                    return geocoded

            print("⚠️ Could not geocode address")
            return None

        except Exception as e:
            print(f"❌ Geocoding error: {e}")
            return None

    def batch_geocode(self, addresses: List[str]) -> List[Dict[str, Any]]:
        """Geocode multiple addresses with rate limiting"""
        results = []

        for address in addresses:
            result = self.geocode_address(address)
            results.append({
                'address': address,
                'geocoded': result
            })

            # Rate limiting: wait between requests
            time.sleep(self.rate_limit_delay)

        return results

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        R = 6371  # Earth's radius in km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance

    def find_nearest_location(self, target_lat: float, target_lon: float, locations: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find nearest location from a list of locations"""
        if not locations:
            return None

        nearest = None
        min_distance = float('inf')

        for location in locations:
            if 'latitude' in location and 'longitude' in location:
                distance = self.calculate_distance(
                    target_lat,
                    target_lon,
                    location['latitude'],
                    location['longitude']
                )

                if distance < min_distance:
                    min_distance = distance
                    nearest = {**location, 'distance_km': distance}

        return nearest

    def check_health(self) -> bool:
        """Check if geocoding service is healthy"""
        try:
            # Test with a simple address
            test_result = self.geocode_address("San Francisco, CA")
            return test_result is not None
        except Exception:
            return False
