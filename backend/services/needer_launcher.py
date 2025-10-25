# py_backend/services/needer_launcher.py
from __future__ import annotations
import os, json, subprocess, shlex, time
from typing import Dict, Any, List

def _env_from_extracted(d: Dict[str, Any]) -> Dict[str, str]:
    lat = os.getenv("NEED_LAT", "37.8715")
    lon = os.getenv("NEED_LON", "-122.2730")
    label = str(d.get("location") or os.getenv("NEED_LABEL", "Request Location"))
    priority = str(d.get("priority") or "medium")
    max_eta_h = str(d.get("max_eta_hours") or os.getenv("NEED_MAX_ETA_H", "6"))

    # items → Item JSON list used by need_agent
    qty = d.get("quantity_needed")
    if isinstance(qty, str) and qty.lower() in {"low","medium","high"}:
        # fallback heuristic (low=50, medium=150, high=300)
        qty_map = {"low": 50, "medium": 150, "high": 300}
        qty = qty_map[qty.lower()]
    if not isinstance(qty, int):
        qty = 100

    names: List[str] = [str(x) for x in (d.get("items") or [])]
    if not names:
        names = ["blanket"]

    # default unit "ea"
    items = [{"name": n.lower(), "qty": qty, "unit": "ea"} for n in names]

    env = {
        "NEED_LAT": os.getenv("NEED_LAT", lat),
        "NEED_LON": os.getenv("NEED_LON", lon),
        "NEED_LABEL": label,
        "NEED_PRIORITY": priority,
        "NEED_MAX_ETA_H": str(max_eta_h),
        "NEED_ITEMS_JSON": json.dumps(items),
        "NEEDER_SEED": d.get("request_id", f"need_{int(time.time())}"),
    }
    # respect externally provided SUPPLY_ADDRS, TELEMETRY_URL, QUOTE_WAIT_S/QUOTE_MAX_WAIT_S etc.
    passthrough = ["SUPPLY_ADDRS","TELEMETRY_URL","QUOTE_WAIT_S","QUOTE_MAX_WAIT_S","UAGENTS_LOG_LEVEL","PYTHONUNBUFFERED","INV_DB_PATH"]
    for k in passthrough:
        if os.getenv(k):
            env[k] = os.getenv(k)
    return env

def launch_needer(extracted: Dict[str, Any], port: int = 0) -> Dict[str, Any]:
    """
    Spawns `python -m agents.need_agent` with env constructed from extracted JSON.
    Returns pid/port and the computed env bits for debugging.
    """
    env = os.environ.copy()
    patch = _env_from_extracted(extracted)
    env.update(patch)

    # select port if provided else 0 → need_agent default/ENV
    if port:
        env["NEEDER_PORT"] = str(port)

    cmd = "python -m agents.need_agent"
    proc = subprocess.Popen(shlex.split(cmd), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {
        "pid": proc.pid,
        "needer_port": int(env.get("NEEDER_PORT") or 0) or "auto",
        "items_env": env.get("NEED_ITEMS_JSON"),
        "priority": env.get("NEED_PRIORITY"),
        "label": env.get("NEED_LABEL"),
    }
