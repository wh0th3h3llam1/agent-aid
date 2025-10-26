#!/usr/bin/env python3
"""
Supply Agent with Message Broker Pattern
Polls Claude service for requests instead of waiting for messages
"""
import os
import json
import math
import asyncio
import httpx
from typing import List, Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.inventory_db import (
    connect,
    ensure_supplier,
    get_supplier_config,
    get_inventory,
    offer_for_request,
    deduct_allocation,
)

# ---------- CONFIG ----------
DB_PATH = os.getenv("INV_DB_PATH", "db/agent_aid.db")
SUPPLIER_NAME = os.getenv("SUPPLIER_NAME", "supply_sf_store_1")
SUPPLIER_PORT = int(os.getenv("SUPPLIER_PORT", "8001"))

# Claude service URL
CLAUDE_SERVICE_URL = os.getenv("CLAUDE_SERVICE_URL", "http://localhost:3000")

# Supplier configuration
SUPPLIER_LAT = float(os.getenv("SUPPLIER_LAT", "37.7749"))
SUPPLIER_LON = float(os.getenv("SUPPLIER_LON", "-122.4194"))
SUPPLIER_LABEL = os.getenv("SUPPLIER_LABEL", "Supply Depot")
SUPPLIER_LEAD_H = float(os.getenv("SUPPLIER_LEAD_H", "1.0"))
SUPPLIER_RADIUS_KM = float(os.getenv("SUPPLIER_RADIUS_KM", "150.0"))
SUPPLIER_DELIVERY_MODE = os.getenv("SUPPLIER_DELIVERY_MODE", "truck")

# ---------- Database ----------
CONN = connect(DB_PATH)
SUPPLIER_ID = None
CFG = {}

# ---------- Utils ----------
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in km between two points"""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

def initialize_supplier():
    """Initialize supplier in database"""
    global SUPPLIER_ID, CFG
    
    SUPPLIER_ID = ensure_supplier(
        CONN,
        SUPPLIER_NAME,
        SUPPLIER_LAT,
        SUPPLIER_LON,
        SUPPLIER_LABEL,
        SUPPLIER_LEAD_H,
        SUPPLIER_RADIUS_KM,
        SUPPLIER_DELIVERY_MODE,
    )
    CFG = get_supplier_config(CONN, SUPPLIER_NAME) or {}
    inv = get_inventory(CONN, SUPPLIER_ID)
    
    print(f"✅ [{SUPPLIER_LABEL}] Initialized")
    print(f"   Supplier ID: {SUPPLIER_ID}")
    print(f"   Location: ({SUPPLIER_LAT}, {SUPPLIER_LON})")
    inv_str = ', '.join([f"{r['name']}:{r['qty']}" for r in inv]) if inv else '(empty)'
    print(f"   Inventory: {inv_str}")

async def process_request(request_data: Dict[str, Any]) -> bool:
    """Process a single request and send quote"""
    request_id = request_data.get("request_id")
    items = request_data.get("items", [])
    location = request_data.get("location", {})
    coordinates = location.get("coordinates", {})
    
    print(f"\n📦 [{SUPPLIER_LABEL}] Processing request: {request_id}")
    print(f"   Items: {items}")
    
    # Check if within radius
    if coordinates:
        req_lat = coordinates.get("latitude", 0)
        req_lon = coordinates.get("longitude", 0)
        distance_km = haversine_km(SUPPLIER_LAT, SUPPLIER_LON, req_lat, req_lon)
        
        print(f"   Distance: {distance_km:.1f} km")
        
        if distance_km > SUPPLIER_RADIUS_KM:
            print(f"   ❌ Out of radius ({SUPPLIER_RADIUS_KM} km)")
            return False
    
    # Check inventory and create quote
    requested = []
    for item_name in items:
        # Try to parse quantity from request
        qty = int(request_data.get("quantity", "1"))
        requested.append({"name": item_name, "qty": qty})
    
    offered, coverage = offer_for_request(CONN, SUPPLIER_ID, requested)
    
    if coverage <= 0.0 or not offered:
        print(f"   ❌ No coverage (inventory insufficient)")
        return False
    
    # Calculate pricing
    total_cost = sum(float(it.get("unit_price", 0.0)) * int(it["qty"]) for it in offered)
    
    # Calculate ETA
    base_lead_h = float(CFG.get("base_lead_h", 1.0))
    if coordinates:
        travel_h = distance_km / 60.0  # Assume 60 km/h
        eta_hours = base_lead_h + travel_h
    else:
        eta_hours = base_lead_h
    
    print(f"   ✅ Can fulfill: {coverage*100:.0f}% coverage")
    print(f"   Cost: ${total_cost:.2f}")
    print(f"   ETA: {eta_hours:.1f} hours")
    
    # Send update to Claude service
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            update_data = {
                "request_id": request_id,
                "agent_id": SUPPLIER_NAME,
                "agent_type": "supply",
                "type": "quote",
                "message": f"Quote from {SUPPLIER_LABEL}",
                "data": {
                    "supplier_id": SUPPLIER_NAME,
                    "supplier_label": SUPPLIER_LABEL,
                    "coverage": coverage,
                    "items": offered,
                    "total_cost": total_cost,
                    "eta_hours": eta_hours,
                    "delivery_mode": CFG.get("delivery_mode", "truck")
                }
            }
            
            response = await client.post(
                f"{CLAUDE_SERVICE_URL}/api/uagent/update",
                json=update_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Quote sent to Claude service")
                return True
            else:
                print(f"   ❌ Failed to send quote: HTTP {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error sending quote: {e}")
        return False

async def poll_for_requests():
    """Poll Claude service for pending requests"""
    print(f"\n🔄 [{SUPPLIER_LABEL}] Starting polling loop...")
    print(f"   Polling: {CLAUDE_SERVICE_URL}/api/uagent/pending-requests")
    print(f"   Interval: 5 seconds\n")
    
    processed_requests = set()
    
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{CLAUDE_SERVICE_URL}/api/uagent/pending-requests")
                
                if response.status_code == 200:
                    data = response.json()
                    requests = data.get("requests", [])
                    
                    if requests:
                        print(f"📋 [{SUPPLIER_LABEL}] Found {len(requests)} pending request(s)")
                        
                        for request_data in requests:
                            request_id = request_data.get("request_id")
                            
                            # Skip if already processed
                            if request_id in processed_requests:
                                continue
                            
                            # Process the request
                            success = await process_request(request_data)
                            
                            if success:
                                processed_requests.add(request_id)
                                
                                # Claim the request
                                try:
                                    claim_response = await client.post(
                                        f"{CLAUDE_SERVICE_URL}/api/uagent/claim-request",
                                        json={
                                            "request_id": request_id,
                                            "agent_id": SUPPLIER_NAME,
                                            "agent_address": f"supply_{SUPPLIER_NAME}"
                                        }
                                    )
                                    if claim_response.status_code == 200:
                                        print(f"   ✅ Claimed request {request_id}")
                                except Exception as e:
                                    print(f"   ⚠️  Could not claim request: {e}")
                    
        except Exception as e:
            print(f"❌ [{SUPPLIER_LABEL}] Error polling: {e}")
        
        # Wait before next poll
        await asyncio.sleep(5)

async def main():
    """Main entry point"""
    print("=" * 60)
    print(f"🚀 Supply Agent: {SUPPLIER_LABEL}")
    print("=" * 60)
    
    # Initialize supplier
    initialize_supplier()
    
    # Start polling
    await poll_for_requests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n👋 [{SUPPLIER_LABEL}] Shutting down...")
