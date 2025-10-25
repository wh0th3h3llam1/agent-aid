#!/usr/bin/env bash
# elastic/bootstrap.sh
set -euo pipefail

: "${ES_URL:=https://my-elasticsearch-project-b5bb84.es.us-west-2.aws.elastic.cloud/}"
: "${ES_API_KEY:=bEtYb0hKb0Jmb09sVUNqMnRMcXc6SXJTRi05emJxQXBheGhQTEE5YTFidw==}"

hdr=(-H 'Content-Type: application/json')
if [[ -n "$ES_API_KEY" ]]; then
  hdr+=(-H "Authorization: ApiKey $ES_API_KEY")
fi

curl -sS -X PUT "$ES_URL/_index_template/agentaid-intel-template" "${hdr[@]}" -d @- <<'JSON'
{
  "index_patterns": ["agentaid-intel-events*"],
  "data_stream": {},
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": {"type": "date"},
        "type": {"type": "keyword"},
        "severity": {"type": "keyword"},
        "event": {"type": "keyword"},
        "headline": {"type": "text"},
        "area": {"type": "keyword"},
        "lat": {"type": "float"},
        "lon": {"type": "float"},
        "qty": {"type": "integer"},
        "unit_price": {"type": "float"},
        "store_id": {"type": "keyword"},
        "store_name": {"type": "keyword"},
        "source_url": {"type": "keyword","ignore_above":2048}
      }
    }
  },
  "priority": 200
}
JSON

curl -sS -X PUT "$ES_URL/_index_template/agentaid-telemetry-template" "${hdr[@]}" -d @- <<'JSON'
{
  "index_patterns": ["agentaid-telemetry*"],
  "data_stream": {},
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": {"type": "date"},
        "agent_type": {"type": "keyword"},
        "agent_id": {"type": "keyword"},
        "event_type": {"type": "keyword"},
        "need_id": {"type": "keyword"},
        "supplier_id": {"type": "keyword"},
        "lat": {"type": "float"},
        "lon": {"type": "float"},
        "duration_ms": {"type": "float"},
        "meta": {"type": "flattened"}
      }
    }
  },
  "priority": 200
}
JSON

echo "✅ Elastic index templates installed."
