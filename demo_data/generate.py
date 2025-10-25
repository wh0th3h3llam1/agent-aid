# demo_data/generate.py
import os, time, random, asyncio, httpx

TELEMETRY_URL = os.getenv("TELEMETRY_URL", "http://127.0.0.1:8088/ingest")

def now(): return time.time()

async def main():
    async with httpx.AsyncClient(timeout=3) as c:
        for i in range(80):
            need_id = f"need_demo_{i:03d}"
            lat, lon = 37.87 + random.uniform(-0.05, 0.05), -122.27 + random.uniform(-0.05, 0.05)
            await c.post(TELEMETRY_URL, json={
                "ts": now(), "agent_type":"needer","agent_id":"demo_needer",
                "event_type":"quote_request","need_id":need_id,"lat":lat,"lon":lon
            })
            dur_ms = random.uniform(150, 2500)
            await c.post(TELEMETRY_URL, json={
                "ts": now(), "agent_type":"needer","agent_id":"demo_needer",
                "event_type":"quote_response","need_id":need_id,"supplier_id":"demo_sup",
                "duration_ms": dur_ms, "lat":lat,"lon":lon,
                "meta":{"coverage": random.choice([0.4,0.6,0.8,1.0]), "total_cost": round(random.uniform(120,1100),2)}
            })
            if i % 3 == 0:
                await c.post(TELEMETRY_URL, json={
                    "ts": now(), "agent_type":"needer","agent_id":"demo_needer",
                    "event_type":"accept_sent","need_id":need_id,"supplier_id":"demo_sup",
                    "lat":lat,"lon":lon
                })
            await asyncio.sleep(0.05)

if __name__ == "__main__":
    asyncio.run(main())
