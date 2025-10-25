# telemetry_ingest/app.py
import os
from typing import Optional, Dict, Any, Literal
from fastapi import FastAPI
from pydantic import BaseModel
from elasticsearch import Elasticsearch

ES_URL = os.getenv("ES_URL", "https://my-elasticsearch-project-b5bb84.es.us-west-2.aws.elastic.cloud/")
ES_API_KEY = os.getenv("bEtYb0hKb0Jmb09sVUNqMnRMcXc6SXJTRi05emJxQXBheGhQTEE5YTFidw==")
TELEMETRY_INDEX = os.getenv("TELEMETRY_INDEX", "agentaid-telemetry")
ES_ACCEPT = os.getenv("ES_ACCEPT", "application/vnd.elasticsearch+json; compatible-with=8")
ES_CT     = os.getenv("ES_CT",     "application/vnd.elasticsearch+json; compatible-with=8")


_DEFAULT_HEADERS = {
    "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
    "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8",
}


if ES_API_KEY:
    es = Elasticsearch(ES_URL, api_key=ES_API_KEY, headers=_DEFAULT_HEADERS, request_timeout=30)
else:
    es = Elasticsearch(ES_URL, headers=_DEFAULT_HEADERS, request_timeout=30)

app = FastAPI(title="AgentAid Telemetry Ingest")

def es_client() -> Elasticsearch:
    headers = {"Accept": ES_ACCEPT, "Content-Type": ES_CT}
    if ES_API_KEY:
        return Elasticsearch(ES_URL, api_key=ES_API_KEY, headers=headers, request_timeout=30)
    return Elasticsearch(ES_URL, headers=headers, request_timeout=30)

class AgentEvent(BaseModel):
    ts: float
    agent_type: Literal["needer","supplier"]
    agent_id: str
    event_type: Literal["quote_request","quote_response","accept_sent","allocation_notice","error"]
    need_id: Optional[str] = None
    supplier_id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    duration_ms: Optional[float] = None

@app.get("/health")
async def health():
    return {"status":"ok"}

@app.post("/ingest")
async def ingest(ev: AgentEvent):
    doc = ev.dict()
    doc["@timestamp"] = int(ev.ts * 1000)
    es.index(index=TELEMETRY_INDEX, document=doc)
    return {"ok": True}
