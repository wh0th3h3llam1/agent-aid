#!/usr/bin/env python3
"""
Need Agent with Negotiation and Selection Logic
Polls for requests, broadcasts to suppliers, evaluates quotes, selects best
"""
import os
import asyncio
import httpx
from typing import List, Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------- CONFIG ----------
NEED_AGENT_NAME = os.getenv("NEED_AGENT_NAME", "need_agent_coordinator")
NEED_AGENT_PORT = int(os.getenv("NEED_AGENT_PORT", "8000"))
CLAUDE_SERVICE_URL = os.getenv("CLAUDE_SERVICE_URL", "http://localhost:3000")

# Evaluation weights for quote selection
WEIGHT_COST = 0.4
WEIGHT_ETA = 0.3
WEIGHT_COVERAGE = 0.3

print(f"🤖 Need Agent: {NEED_AGENT_NAME}")
print(f"   Polling: {CLAUDE_SERVICE_URL}")
print(f"   Evaluation: Cost={WEIGHT_COST}, ETA={WEIGHT_ETA}, Coverage={WEIGHT_COVERAGE}")

# Track processed requests
processed_requests = set()
pending_negotiations = {}  # request_id -> negotiation state

async def evaluate_quote(quote: Dict[str, Any], request_data: Dict[str, Any]) -> float:
    """
    Evaluate a quote and return a score (higher is better)
    
    Factors:
    - Cost (lower is better)
    - ETA (faster is better)
    - Coverage (100% is best)
    """
    quote_data = quote.get('data', {})
    
    # Extract quote details
    total_cost = float(quote_data.get('total_cost', 999999))
    eta_hours = float(quote_data.get('eta_hours', 999))
    coverage = float(quote_data.get('coverage', 0))
    
    # Normalize scores (0-1, higher is better)
    # Cost: inverse normalized (cheaper is better)
    cost_score = 1.0 / (1.0 + total_cost / 1000.0)
    
    # ETA: inverse normalized (faster is better)
    eta_score = 1.0 / (1.0 + eta_hours / 10.0)
    
    # Coverage: already 0-1 (100% = 1.0)
    coverage_score = coverage
    
    # Weighted total score
    total_score = (
        WEIGHT_COST * cost_score +
        WEIGHT_ETA * eta_score +
        WEIGHT_COVERAGE * coverage_score
    )
    
    return total_score

async def negotiate_with_suppliers(request_id: str, quotes: List[Dict[str, Any]], request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Negotiate with suppliers and select the best quote
    
    Returns:
    - Selected supplier
    - Negotiation details
    - Reasoning
    """
    print(f"\n🤝 [{NEED_AGENT_NAME}] Negotiating for request: {request_id}")
    print(f"   Received {len(quotes)} quote(s)")
    
    if not quotes:
        return {
            'success': False,
            'reason': 'No quotes received'
        }
    
    # Evaluate each quote
    evaluated_quotes = []
    for quote in quotes:
        score = await evaluate_quote(quote, request_data)
        quote_data = quote.get('data', {})
        
        evaluated_quotes.append({
            'quote': quote,
            'score': score,
            'supplier': quote_data.get('supplier_label', quote.get('agent_id')),
            'cost': quote_data.get('total_cost', 0),
            'eta': quote_data.get('eta_hours', 0),
            'coverage': quote_data.get('coverage', 0)
        })
        
        print(f"   📊 {quote_data.get('supplier_label', 'Unknown')}")
        print(f"      Cost: ${quote_data.get('total_cost', 0)}")
        print(f"      ETA: {quote_data.get('eta_hours', 0):.1f} hours")
        print(f"      Coverage: {quote_data.get('coverage', 0)*100:.0f}%")
        print(f"      Score: {score:.3f}")
    
    # Sort by score (highest first)
    evaluated_quotes.sort(key=lambda x: x['score'], reverse=True)
    
    # Select best quote
    best = evaluated_quotes[0]
    
    print(f"\n   ✅ Selected: {best['supplier']}")
    print(f"      Reason: Best overall score ({best['score']:.3f})")
    print(f"      Cost: ${best['cost']}")
    print(f"      ETA: {best['eta']:.1f} hours")
    
    # Prepare negotiation result
    result = {
        'success': True,
        'selected_supplier': best['quote'].get('agent_id'),
        'selected_quote': best['quote'],
        'score': best['score'],
        'all_quotes': evaluated_quotes,
        'reasoning': f"Selected {best['supplier']} with score {best['score']:.3f}. "
                    f"Best balance of cost (${best['cost']}), speed ({best['eta']:.1f}h), "
                    f"and coverage ({best['coverage']*100:.0f}%)."
    }
    
    return result

async def send_negotiation_update(request_id: str, negotiation_result: Dict[str, Any]):
    """Send negotiation result back to Claude service"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            update_data = {
                'request_id': request_id,
                'agent_id': NEED_AGENT_NAME,
                'agent_type': 'need',
                'type': 'negotiation_complete',
                'message': f'Negotiation complete - Selected best supplier',
                'data': {
                    'selected_supplier': negotiation_result.get('selected_supplier'),
                    'score': negotiation_result.get('score'),
                    'reasoning': negotiation_result.get('reasoning'),
                    'quote_count': len(negotiation_result.get('all_quotes', []))
                }
            }
            
            response = await client.post(
                f"{CLAUDE_SERVICE_URL}/api/uagent/update",
                json=update_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Negotiation result sent to Claude service")
                return True
            else:
                print(f"   ❌ Failed to send result: HTTP {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error sending result: {e}")
        return False

async def send_allocation_request(request_id: str, selected_quote: Dict[str, Any]):
    """Send allocation confirmation to selected supplier"""
    try:
        supplier_id = selected_quote.get('agent_id')
        quote_data = selected_quote.get('data', {})
        
        async with httpx.AsyncClient(timeout=10) as client:
            allocation_data = {
                'request_id': request_id,
                'agent_id': NEED_AGENT_NAME,
                'agent_type': 'need',
                'type': 'allocation_request',
                'message': f'Requesting allocation from {supplier_id}',
                'data': {
                    'supplier_id': supplier_id,
                    'items': quote_data.get('items', []),
                    'total_cost': quote_data.get('total_cost'),
                    'eta_hours': quote_data.get('eta_hours')
                }
            }
            
            response = await client.post(
                f"{CLAUDE_SERVICE_URL}/api/uagent/update",
                json=allocation_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Allocation request sent")
                return True
                
    except Exception as e:
        print(f"   ❌ Error sending allocation: {e}")
        return False

async def process_request(request_data: Dict[str, Any]) -> bool:
    """Process a single request - wait for quotes and negotiate"""
    request_id = request_data.get('request_id')
    
    if request_id in processed_requests:
        return False
    
    print(f"\n📋 [{NEED_AGENT_NAME}] Processing request: {request_id}")
    print(f"   Items: {request_data.get('items', [])}")
    print(f"   Location: {request_data.get('location', {}).get('address', 'Unknown')}")
    
    # Mark as being processed
    pending_negotiations[request_id] = {
        'request_data': request_data,
        'start_time': asyncio.get_event_loop().time(),
        'quotes_collected': []
    }
    
    # Wait for quotes (give suppliers time to respond)
    print(f"   ⏳ Waiting 10 seconds for supplier quotes...")
    await asyncio.sleep(10)
    
    # Fetch quotes from Claude service
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{CLAUDE_SERVICE_URL}/api/uagent/updates")
            
            if response.status_code == 200:
                data = response.json()
                all_updates = data.get('updates', [])
                
                # Filter quotes for this request
                quotes = [
                    u for u in all_updates
                    if u.get('request_id') == request_id and u.get('type') == 'quote'
                ]
                
                if quotes:
                    # Negotiate and select best quote
                    negotiation_result = await negotiate_with_suppliers(request_id, quotes, request_data)
                    
                    if negotiation_result.get('success'):
                        # Send negotiation result
                        await send_negotiation_update(request_id, negotiation_result)
                        
                        # Send allocation request to selected supplier
                        await send_allocation_request(request_id, negotiation_result['selected_quote'])
                        
                        # Mark as processed
                        processed_requests.add(request_id)
                        del pending_negotiations[request_id]
                        
                        return True
                else:
                    print(f"   ⚠️  No quotes received yet")
                    
    except Exception as e:
        print(f"   ❌ Error processing request: {e}")
    
    return False

async def poll_for_requests():
    """Poll Claude service for pending requests"""
    print(f"\n🔄 [{NEED_AGENT_NAME}] Starting polling loop...")
    print(f"   Interval: 8 seconds\n")
    
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{CLAUDE_SERVICE_URL}/api/uagent/pending-requests")
                
                if response.status_code == 200:
                    data = response.json()
                    requests = data.get('requests', [])
                    
                    if requests:
                        print(f"📋 [{NEED_AGENT_NAME}] Found {len(requests)} pending request(s)")
                        
                        for request_data in requests:
                            request_id = request_data.get('request_id')
                            
                            # Skip if already processed or being processed
                            if request_id not in processed_requests and request_id not in pending_negotiations:
                                # Process in background
                                asyncio.create_task(process_request(request_data))
                    
        except Exception as e:
            print(f"❌ [{NEED_AGENT_NAME}] Error polling: {e}")
        
        # Wait before next poll
        await asyncio.sleep(8)

async def main():
    """Main entry point"""
    print("=" * 60)
    print(f"🤖 Need Agent with Negotiation")
    print("=" * 60)
    print(f"   Agent: {NEED_AGENT_NAME}")
    print(f"   Service: {CLAUDE_SERVICE_URL}")
    print(f"   Role: Coordinate suppliers, negotiate, select best quote")
    print("=" * 60)
    
    # Start polling
    await poll_for_requests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n👋 [{NEED_AGENT_NAME}] Shutting down...")
