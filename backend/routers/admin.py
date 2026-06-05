from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid

from dependencies import get_current_user, get_admin_user
from services.supabase_client import supabase
from config import DEFAULT_AUTO_APPROVE_MAX, DEFAULT_MANUAL_REVIEW_MIN, DEFAULT_AUTO_REJECT_MIN

# Import from feed router to access reboot requests
from routers.feed import _LOCAL_REBOOT_REQUESTS

router = APIRouter()

# In-memory fallback
_thresholds = {
    "id": "default",
    "auto_approve_max":  DEFAULT_AUTO_APPROVE_MAX,
    "manual_review_min": DEFAULT_MANUAL_REVIEW_MIN,
    "auto_reject_min":   DEFAULT_AUTO_REJECT_MIN,
    "updated_at": datetime.utcnow().isoformat() + "Z",
}
_queue = []
_logs  = []


# ---- Thresholds ------------------------------------------------

@router.get("/thresholds")
async def get_thresholds(user=Depends(get_current_user)):
    if supabase:
        res = supabase.table("thresholds").select("*").limit(1).execute()
        return res.data[0] if res.data else _thresholds
    return _thresholds


class ThresholdUpdate(BaseModel):
    auto_approve_max: int
    manual_review_min: int
    auto_reject_min: int


@router.put("/thresholds")
async def update_thresholds(body: ThresholdUpdate, admin=Depends(get_admin_user)):
    if body.auto_approve_max >= body.auto_reject_min:
        raise HTTPException(status_code=400, detail="auto_approve_max must be less than auto_reject_min")

    updated = {
        "auto_approve_max":  body.auto_approve_max,
        "manual_review_min": body.manual_review_min,
        "auto_reject_min":   body.auto_reject_min,
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }

    if supabase:
        res = supabase.table("thresholds").select("id").limit(1).execute()
        if res.data:
            supabase.table("thresholds").update(updated).eq("id", res.data[0]["id"]).execute()
        else:
            supabase.table("thresholds").insert(updated).execute()

        supabase.table("admin_logs").insert({
            "id": str(uuid.uuid4()),
            "admin_id": admin["id"],
            "action": f"threshold_update: approve<={body.auto_approve_max}, reject>={body.auto_reject_min}",
            "payload": updated,
            "logged_at": datetime.utcnow().isoformat() + "Z",
        }).execute()
    else:
        _thresholds.update(updated)
        _logs.append({
            "action": f"Threshold update: approve<={body.auto_approve_max}, reject>={body.auto_reject_min}",
            "actor_email": admin["email"],
            "actor_role": "admin",
            "logged_at": datetime.utcnow().isoformat() + "Z",
        })

    return {"message": "Thresholds updated", **updated}


# ---- Moderation queue ------------------------------------------

@router.get("/queue")
async def get_queue(admin=Depends(get_admin_user)):
    if supabase:
        res = supabase.table("moderation_queue") \
            .select("*").is_("decision", "null") \
            .order("reviewed_at", desc=True).limit(50).execute()
        return {"items": res.data or []}
    return {"items": _queue}


class DecisionBody(BaseModel):
    decision: str  # 'approved' | 'rejected'
    reviewer_note: str = ""


@router.post("/queue/{queue_id}/decide")
async def decide(queue_id: str, body: DecisionBody, admin=Depends(get_admin_user)):
    if body.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="decision must be 'approved' or 'rejected'")

    now = datetime.utcnow().isoformat() + "Z"

    if supabase:
        supabase.table("moderation_queue").update({
            "decision": body.decision,
            "reviewer_note": body.reviewer_note,
            "reviewed_at": now,
        }).eq("id", queue_id).execute()

        supabase.table("admin_logs").insert({
            "id": str(uuid.uuid4()),
            "admin_id": admin["id"],
            "action": f"queue_decision: {body.decision} on {queue_id}",
            "payload": {"queue_id": queue_id, "decision": body.decision},
            "logged_at": now,
        }).execute()
    else:
        for item in _queue:
            if item["id"] == queue_id:
                item["decision"] = body.decision
                item["reviewed_at"] = now
        _logs.append({
            "action": f"Queue decision: {body.decision}",
            "actor_email": admin["email"],
            "actor_role": "admin",
            "logged_at": now,
        })

    return {"message": f"Marked as {body.decision}"}


# ---- Users ------------------------------------------------------

@router.get("/users")
async def list_users(admin=Depends(get_admin_user)):
    if supabase:
        res = supabase.table("users").select("id,email,role,created_at") \
            .order("created_at", desc=True).execute()
        return {"users": res.data or []}

    return {"users": [
        {"id": "demo-user-001",  "email": "user@demo.com",  "role": "user",  "created_at": "2025-01-01T00:00:00Z"},
        {"id": "demo-admin-001", "email": "admin@demo.com", "role": "admin", "created_at": "2025-01-01T00:00:00Z"},
    ]}


# ---- Logs -------------------------------------------------------

@router.get("/logs")
async def list_logs(admin=Depends(get_admin_user)):
    if supabase:
        res = supabase.table("admin_logs").select("*") \
            .order("logged_at", desc=True).limit(50).execute()
        raw = res.data or []
        # Enrich with actor email
        logs = []
        for l in raw:
            actor = None
            if l.get("admin_id"):
                ur = supabase.table("users").select("email,role").eq("id", l["admin_id"]).execute()
                actor = ur.data[0] if ur.data else None
            logs.append({
                "action": l["action"],
                "actor_email": actor["email"] if actor else "system",
                "actor_role":  actor["role"]  if actor else "system",
                "logged_at":   l["logged_at"],
            })
        return {"logs": logs}

    return {"logs": list(reversed(_logs))}


# ---- Feed Reboot Requests -----------------------------------

@router.get("/reboot-requests")
async def list_reboot_requests(admin=Depends(get_admin_user)):
    """Admin view all feed reboot requests."""
    if supabase:
        # TODO: Query from database
        pass
    
    return {"requests": _LOCAL_REBOOT_REQUESTS}


@router.post("/reboot-requests/{request_id}/approve")
async def approve_reboot_request(request_id: str, admin=Depends(get_admin_user)):
    """Admin approves a feed reboot request."""
    now = datetime.utcnow().isoformat() + "Z"
    
    # Find and update request
    for req in _LOCAL_REBOOT_REQUESTS:
        if req["id"] == request_id:
            req["status"] = "approved"
            req["approved_by"] = admin["id"]
            req["approved_at"] = now
            
            # Log the action
            _logs.append({
                "action": f"Feed reboot approved for @{req['instagram_username']}",
                "actor_email": admin["email"],
                "actor_role": "admin",
                "logged_at": now,
            })
            
            # TODO: Actually execute Instagram API feed reboot here
            
            return {
                "message": f"Feed reboot approved for @{req['instagram_username']}",
                "request_id": request_id,
                "status": "approved"
            }
    
    raise HTTPException(status_code=404, detail="Request not found")


@router.post("/reboot-requests/{request_id}/reject")
async def reject_reboot_request(request_id: str, admin=Depends(get_admin_user)):
    """Admin rejects a feed reboot request."""
    now = datetime.utcnow().isoformat() + "Z"
    
    # Find and update request
    for req in _LOCAL_REBOOT_REQUESTS:
        if req["id"] == request_id:
            req["status"] = "rejected"
            req["rejected_by"] = admin["id"]
            req["rejected_at"] = now
            
            # Log the action
            _logs.append({
                "action": f"Feed reboot rejected for @{req['instagram_username']}",
                "actor_email": admin["email"],
                "actor_role": "admin",
                "logged_at": now,
            })
            
            return {
                "message": f"Feed reboot rejected for @{req['instagram_username']}",
                "request_id": request_id,
                "status": "rejected"
            }
    
    raise HTTPException(status_code=404, detail="Request not found")
