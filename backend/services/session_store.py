# py_backend/services/session_store.py
from __future__ import annotations
from typing import Dict, Any
import time
import threading
import uuid

_store: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()

def create_session(payload: Dict[str, Any], ttl_sec: int = 1800) -> str:
    sid = f"SESSION-{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}"
    with _lock:
        _store[sid] = {"data": payload, "expires_at": time.time() + ttl_sec}
    return sid

def get_session(sid: str) -> Dict[str, Any] | None:
    with _lock:
        rec = _store.get(sid)
        if not rec:
            return None
        if rec["expires_at"] < time.time():
            _store.pop(sid, None)
            return None
        return rec["data"]

def delete_session(sid: str):
    with _lock:
        _store.pop(sid, None)
