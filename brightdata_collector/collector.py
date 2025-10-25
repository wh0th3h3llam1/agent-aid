# brightdata_collector/collector.py
import os, asyncio, time, httpx
from datetime import datetime, timezone
from typing import List, Dict, Any
from elasticsearch import Elasticsearch
from elastic_transport import ApiError

BRIGHT_DATA_API_KEY = os.getenv("0d618589c8138c69f02216c3faf09ff1a30a73403e474973bfa5c234598c2505")
ES_URL = os.getenv("ES_URL", "https://my-elasticsearch-project-b5bb84.es.us-west-2.aws.elastic.cloud/")
ES_API_KEY = os.getenv("bEtYb0hKb0Jmb09sVUNqMnRMcXc6SXJTRi05emJxQXBheGhQTEE5YTFidw==")
POLL_INTERVAL_S = int(os.getenv("POLL_INTERVAL_S", "60"))
ES_ACCEPT = os.getenv("ES_ACCEPT", "application/vnd.elasticsearch+json; compatible-with=8")
ES_CT     = os.getenv("ES_CT",     "application/vnd.elasticsearch+json; compatible-with=8")


WEATHER_URL = os.getenv("WEATHER_URL", "https://api.weather.gov/alerts/active?status=actual")
ROADS_URL   = os.getenv("ROADS_URL",   "https://api.brightdata.com/dca/roads")      # your BD endpoint
STORES_URL  = os.getenv("STORES_URL",  "https://api.brightdata.com/dca/inventory")  # your BD endpoint

INTEL_INDEX = os.getenv("INTEL_INDEX", "agentaid-intel-events")

def es_client() -> Elasticsearch:
    if ES_API_KEY:
        return Elasticsearch(ES_URL, api_key=ES_API_KEY, request_timeout=30)
    return Elasticsearch(ES_URL, request_timeout=30)
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

async def fetch_with_bd_key(client: httpx.AsyncClient, url: str) -> Dict[str, Any]:
    """Fetch JSON via Bright Data Direct Access using Authorization: Bearer <API_KEY>."""
    headers = {"Authorization": f"Bearer {BRIGHT_DATA_API_KEY}"} if BRIGHT_DATA_API_KEY else {}
    try:
        r = await client.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return {"raw": r.text}
    except Exception as e:
        return {"error": str(e), "source_url": url}

def normalize_weather_alerts(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for f in (payload or {}).get("features", []):
        p = f.get("properties", {})
        out.append({
            "@timestamp": now_iso(),
            "type": "weather_alert",
            "severity": p.get("severity"),
            "event": p.get("event"),
            "headline": p.get("headline"),
            "area": p.get("areaDesc"),
            "sent": p.get("sent"),
            "effective": p.get("effective"),
            "expires": p.get("expires"),
            "source_url": p.get("source") or "https://api.weather.gov/alerts/active"
        })
    return out

def normalize_roads(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for c in (payload or {}).get("closures", []):
        out.append({
            "@timestamp": now_iso(),
            "type": "road_block",
            "road": c.get("road"),
            "status": c.get("status", "closed"),
            "reason": c.get("reason"),
            "lat": c.get("lat"),
            "lon": c.get("lon"),
            "source_url": (payload or {}).get("source") or "dca/roads"
        })
    return out

def normalize_inventory(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for s in (payload or {}).get("stores", []):
        for i in s.get("inventory", []):
            out.append({
                "@timestamp": now_iso(),
                "type": "store_inventory",
                "store_id": s.get("id"),
                "store_name": s.get("name"),
                "lat": s.get("lat"),
                "lon": s.get("lon"),
                "item": i.get("name"),
                "qty": i.get("qty"),
                "unit_price": i.get("unit_price"),
                "source_url": (payload or {}).get("source") or "dca/inventory"
            })
    return out

async def es_bulk(es: Elasticsearch, index: str, docs: List[Dict[str, Any]]):
    if not docs:
        return
    ops: List[Dict[str, Any]] = []
    for d in docs:
        ops.append({"index": {"_index": index}})
        ops.append(d)
    try:
        es.bulk(operations=ops, refresh=False)
    except ApiError as e:
        print("[collector] Elasticsearch bulk error:", e)

async def main():
    es = es_client()
    async with httpx.AsyncClient() as client:
        while True:
            weather = await fetch_with_bd_key(client, WEATHER_URL)
            roads   = await fetch_with_bd_key(client, ROADS_URL)
            stores  = await fetch_with_bd_key(client, STORES_URL)

            docs: List[Dict[str, Any]] = []
            if "error" not in weather: docs += normalize_weather_alerts(weather)
            if "error" not in roads:   docs += normalize_roads(roads)
            if "error" not in stores:  docs += normalize_inventory(stores)

            await es_bulk(es, INTEL_INDEX, docs)
            print(f"[collector] indexed {len(docs)} events at {time.strftime('%H:%M:%S')}")
            await asyncio.sleep(POLL_INTERVAL_S)

if __name__ == "__main__":
    asyncio.run(main())
