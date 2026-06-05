from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid, random

from dependencies import get_current_user
from services.supabase_client import supabase

router = APIRouter()

_LOCAL_FEEDS = []
_LOCAL_REBOOT_REQUESTS = []

MOCK_POSTS = [
    {"id": "p1", "caption": "Beautiful sunset at Marina Beach!", "category": "nature",   "safety_score": 8,  "date": "2025-06-01T10:00:00Z"},
    {"id": "p2", "caption": "Gym gains this week looking fire",  "category": "fitness",  "safety_score": 22, "date": "2025-06-01T14:00:00Z"},
    {"id": "p3", "caption": "This fight video is insane",        "category": "violence", "safety_score": 84, "date": "2025-06-02T09:00:00Z"},
    {"id": "p4", "caption": "New recipe — avocado toast",        "category": "food",     "safety_score": 5,  "date": "2025-06-02T12:00:00Z"},
    {"id": "p5", "caption": "Controversial thread — unpopular opinion", "category": "opinion", "safety_score": 61, "date": "2025-06-03T08:00:00Z"},
    {"id": "p6", "caption": "Travel vlog: Kodaikanal hills",     "category": "travel",   "safety_score": 11, "date": "2025-06-03T16:00:00Z"},
    {"id": "p7", "caption": "Graphic road accident footage",     "category": "graphic",  "safety_score": 91, "date": "2025-06-04T07:00:00Z"},
    {"id": "p8", "caption": "Morning routine motivation",        "category": "lifestyle","safety_score": 14, "date": "2025-06-04T10:00:00Z"},
    {"id": "p9", "caption": "Hate speech circulating — exposing it", "category": "hate", "safety_score": 75, "date": "2025-06-04T15:00:00Z"},
]


def _score_to_status(score: int) -> str:
    if score >= 80: return "rejected"
    if score >= 50: return "manual_review"
    return "approved"


class AnalyzeBody(BaseModel):
    instagram_username: Optional[str] = None


@router.post("/analyze")
async def analyze_feed(body: AnalyzeBody = None, user=Depends(get_current_user)):
    """Scores the mock feed. Replace MOCK_POSTS with real Instagram feed data."""
    # TODO: Fetch real Instagram feed using instagram_username
    instagram_username = body.instagram_username if body else None
    
    posts = MOCK_POSTS
    scores = [p["safety_score"] for p in posts]
    overall = round(sum(scores) / len(scores))
    status  = _score_to_status(overall)

    record = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "instagram_username": instagram_username,
        "feed_snapshot": posts,
        "overall_score": overall,
        "status": status,
        "analysed_at": datetime.utcnow().isoformat() + "Z",
    }

    if supabase:
        supabase.table("feed_analyses").insert(record).execute()
        if status == "manual_review":
            supabase.table("moderation_queue").insert({
                "id": str(uuid.uuid4()),
                "ref_id": record["id"],
                "ref_type": "feed",
                "score": overall,
            }).execute()
    else:
        _LOCAL_FEEDS.append(record)

    return {"posts": posts, "overall_score": overall, "status": status, "id": record["id"]}


class RebootBody(BaseModel):
    post_ids: List[str]


class RebootRequestBody(BaseModel):
    instagram_username: str
    post_ids: List[str]
    flagged_count: int


@router.post("/reboot-request")
async def request_feed_reboot(body: RebootRequestBody, user=Depends(get_current_user)):
    """User requests feed reboot - goes to admin for approval."""
    request_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    
    request_record = {
        "id": request_id,
        "user_id": user["id"],
        "user_email": user.get("email", ""),
        "instagram_username": body.instagram_username,
        "post_ids": body.post_ids,
        "flagged_count": body.flagged_count,
        "status": "pending",  # pending, approved, rejected
        "requested_at": now,
    }
    
    # Store in database or in-memory
    if supabase:
        # TODO: Create feed_reboot_requests table in database
        pass
    
    _LOCAL_REBOOT_REQUESTS.append(request_record)
    
    return {
        "request_id": request_id,
        "status": "pending",
        "message": f"Feed reboot request submitted for @{body.instagram_username}. Admin will review it soon."
    }


@router.post("/reboot")
async def reboot_feed(body: RebootBody, user=Depends(get_current_user)):
    """Marks specified posts as removed. In production, call Instagram Graph API here."""
    return {
        "removed": len(body.post_ids),
        "post_ids": body.post_ids,
        "message": f"Removed {len(body.post_ids)} flagged post(s) from feed."
    }


@router.get("/reboot-requests")
async def get_reboot_requests(user=Depends(get_current_user)):
    """Get user's feed reboot requests."""
    if supabase:
        # TODO: Query from database
        pass
    
    user_requests = [r for r in _LOCAL_REBOOT_REQUESTS if r["user_id"] == user["id"]]
    return {"requests": user_requests}
