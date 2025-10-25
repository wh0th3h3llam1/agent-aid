# py_backend/app.py
from __future__ import annotations
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.completeness import check_completeness, generate_followup_message, merge_followup
from services.session_store import create_session, get_session, delete_session
from services.needer_launcher import launch_needer

app = FastAPI(title="AgentAid Python Backend")

class ExtractedData(BaseModel):
    items: list[str] = Field(default_factory=list)
    quantity_needed: Optional[int | str] = None
    location: Optional[str] = None
    priority: Optional[str] = "medium"
    contact: Optional[str] = None
    additional_notes: Optional[str] = None
    victim_count: Optional[int] = None
    timestamp: Optional[str] = None
    raw_input: Optional[str] = None
    request_id: Optional[str] = None

class StartBody(BaseModel):
    extractedData: ExtractedData
    userInput: Optional[str] = None

class ReplyBody(BaseModel):
    session_id: str
    followupInput: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/api/assist/start")
def assist_start(body: StartBody):
    data = body.extractedData.dict()
    chk = check_completeness(data)

    if not chk["is_complete"]:
        follow = generate_followup_message(data, body.userInput or data.get("raw_input") or "")
        sid = create_session({"extractedData": data})
        return {
            "success": True,
            "needs_followup": True,
            "followup": {
                "session_id": sid,
                "completeness_score": follow.get("completeness_score", chk["completeness_score"]),
                "issues": follow.get("issues", chk["issues"]),
                "message": follow["message"],
            },
        }

    # complete → launch
    launched = launch_needer(data)
    return {
        "success": True,
        "needs_followup": False,
        "coordinator": launched,
    }

@app.post("/api/assist/reply")
def assist_reply(body: ReplyBody):
    sess = get_session(body.session_id)
    if not sess or "extractedData" not in sess:
        raise HTTPException(status_code=404, detail="session not found or expired")

    merged = merge_followup(sess["extractedData"], body.followupInput)
    chk = check_completeness(merged)
    if not chk["is_complete"]:
        # ask again (rare)
        follow = generate_followup_message(merged, body.followupInput)
        sid = create_session({"extractedData": merged})
        return {
            "success": True,
            "needs_followup": True,
            "followup": {
                "session_id": sid,
                "completeness_score": follow.get("completeness_score"),
                "issues": follow.get("issues"),
                "message": follow["message"],
            },
        }

    launched = launch_needer(merged)
    delete_session(body.session_id)
    return {
        "success": True,
        "needs_followup": False,
        "coordinator": launched,
    }
