# py_backend/services/completeness.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import re
import time
import json

VAGUE_ITEMS = {"medicine", "medical", "supplies", "food", "items", "stuff", "things"}

@dataclass
class Issue:
    type: str
    field: str
    current_value: Any
    question: str

def _has_specific_address(location: Optional[str]) -> bool:
    if not location:
        return False
    patterns = [
        r"\d+\s+\w+(\s+\w+)*\s+(street|st|avenue|ave|road|rd|blvd|drive|dr|lane|ln)\b",
        r"room\s+\d+",
        r"building\s+[\w-]+",
        r"\d+\s+\w+",
        r"\b[A-Z]{2}\s*\d{5}(-\d{4})?\b",  # US ZIP hint
    ]
    return any(re.search(p, location, re.IGNORECASE) for p in patterns)

def _gen_item_specificity_question(items: List[str]) -> str:
    qs: List[str] = []
    for item in items:
        low = str(item).lower()
        if "medicine" in low or "medical" in low:
            qs.append("What specific medicine/medical supplies do you need? (e.g., first-aid kits, bandages, insulin, antibiotics)")
        elif "food" in low:
            qs.append("What specific food items do you need? (e.g., baby formula, canned goods, rice, protein bars)")
        elif "supplies" in low:
            qs.append("What specific supplies do you need? Please list the exact items.")
    if not qs:
        qs.append("Please specify exactly what items you need.")
    return " ".join(qs)

def check_completeness(extracted: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[Issue] = []

    items = [str(x) for x in (extracted.get("items") or [])]
    needs_specificity = any(any(v in i.lower() for v in VAGUE_ITEMS) for i in items)
    if needs_specificity:
        issues.append(Issue(
            type="vague_items",
            field="items",
            current_value=items,
            question=_gen_item_specificity_question(items),
        ))

    qty = extracted.get("quantity_needed")
    if qty is None or (isinstance(qty, str) and qty.lower() in {"low","medium","high"}):
        issues.append(Issue(
            type="vague_quantity",
            field="quantity_needed",
            current_value=qty,
            question=f'Please specify the exact quantity for {", ".join(items) or "your items"} (e.g., "50 units" or "100 bottles").'
        ))

    if not extracted.get("contact"):
        issues.append(Issue(
            type="missing_contact",
            field="contact",
            current_value=None,
            question="Please provide a phone number so we can coordinate delivery."
        ))

    loc = extracted.get("location")
    if not loc or len(str(loc)) < 10 or not _has_specific_address(str(loc)):
        issues.append(Issue(
            type="vague_location",
            field="location",
            current_value=loc,
            question='Please provide a specific address or landmark (e.g., "123 Main St, City" or "Lincoln High School, Room 101").'
        ))

    score_total = 5  # items, quantity, location, contact, priority
    missing = len(issues)
    completeness_score = round(((score_total - missing) / score_total) * 100)

    return {
        "is_complete": missing == 0,
        "issues": [i.__dict__ for i in issues],
        "completeness_score": completeness_score,
    }

def generate_followup_message(extracted: Dict[str, Any], user_input: str) -> Dict[str, Any]:
    """
    Pure-Python follow-up (no external LLM). It concatenates specific questions into one brief message.
    """
    chk = check_completeness(extracted)
    if chk["is_complete"]:
        return {"needs_followup": False, "message": ""}

    prompts = [iss["question"] for iss in chk["issues"]]
    text = (
        "Thanks for reaching out — I’m here to help. To act quickly and correctly, "
        "please share a few details:\n\n- " + "\n- ".join(prompts) +
        "\n\n(You can reply in a single message.)"
    )
    return {
        "needs_followup": True,
        "completeness_score": chk["completeness_score"],
        "issues": chk["issues"],
        "message": text,
    }

def merge_followup(original: Dict[str, Any], followup_input: str) -> Dict[str, Any]:
    """
    Heuristic updater (no LLM). You can later swap in an LLM if you want.
    We try to parse numbers and a phone from the follow-up.
    """
    merged = dict(original)

    # quantity (first integer we see)
    m_qty = re.search(r"\b(\d{1,5})\b", followup_input)
    if m_qty:
        merged["quantity_needed"] = int(m_qty.group(1))

    # phone
    m_phone = re.search(r"(\+?\d[\d\-\s]{7,}\d)", followup_input)
    if m_phone:
        merged["contact"] = m_phone.group(1).strip()

    # items detail (very naive: words like bandage, insulin, kit, etc.)
    keywords = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", followup_input)
    medical_words = {"bandage", "bandages", "first-aid", "first", "aid", "kit", "kits", "insulin", "antibiotics", "gauze", "syringe", "painkiller"}
    if any(w.lower() in medical_words for w in keywords):
        merged["items"] = ["medical supplies"] + sorted({w for w in merged.get("items", []) if w != "medical supplies"})

    # address: if message looks like an address, replace location
    if _has_specific_address(followup_input):
        merged["location"] = followup_input

    merged["follow_up_completed"] = True
    merged["timestamp"] = merged.get("timestamp") or __now_iso()
    # append raw trail
    merged["raw_input"] = f'{original.get("raw_input","")}\n[Follow-up]: {followup_input}'.strip()
    return merged

def __now_iso() -> str:
    import datetime
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
