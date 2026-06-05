from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from datetime import datetime
import uuid

from dependencies import get_current_user
from services.vision_service import analyze_image
from services.supabase_client import supabase

router = APIRouter()

# In-memory store when Supabase is not configured
_LOCAL_CHECKS = []


@router.post("/check")
async def check_image(file: UploadFile = File(...), user=Depends(get_current_user)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 10 MB")

    result = await analyze_image(contents, file.filename or "")

    record = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "image_url": "",  # set to Supabase Storage URL if you upload there
        "safety_score": result["safety_score"],
        "status": result["status"],
        "vision_labels": result["vision_labels"],
        "checked_at": datetime.utcnow().isoformat() + "Z",
    }

    if supabase:
        supabase.table("image_checks").insert(record).execute()

        # Add to moderation queue if needs review
        if result["status"] == "manual_review":
            supabase.table("moderation_queue").insert({
                "id": str(uuid.uuid4()),
                "ref_id": record["id"],
                "ref_type": "image",
                "score": result["safety_score"],
            }).execute()
    else:
        _LOCAL_CHECKS.append(record)

    return record


@router.get("/history")
async def image_history(user=Depends(get_current_user)):
    if supabase:
        res = supabase.table("image_checks") \
            .select("id,safety_score,status,checked_at") \
            .eq("user_id", user["id"]) \
            .order("checked_at", desc=True) \
            .limit(20) \
            .execute()
        return {"items": res.data or []}

    # Local fallback
    items = [c for c in _LOCAL_CHECKS if c["user_id"] == user["id"]]
    items.sort(key=lambda x: x["checked_at"], reverse=True)
    return {"items": items[:20]}
