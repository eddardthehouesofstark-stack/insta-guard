from fastapi import APIRouter, Depends
from dependencies import get_current_user
from services.supabase_client import supabase
from routers.images import _LOCAL_CHECKS
from routers.feed import _LOCAL_FEEDS

router = APIRouter()


@router.get("/stats")
async def stats(user=Depends(get_current_user)):
    uid = user["id"]

    if supabase:
        imgs  = supabase.table("image_checks").select("id,status").eq("user_id", uid).execute().data or []
        feeds = supabase.table("feed_analyses").select("id").eq("user_id", uid).execute().data or []
    else:
        imgs  = [c for c in _LOCAL_CHECKS if c["user_id"] == uid]
        feeds = [f for f in _LOCAL_FEEDS  if f["user_id"] == uid]

    rejected = sum(1 for i in imgs if i.get("status") == "rejected")
    pending  = sum(1 for i in imgs if i.get("status") == "manual_review")

    return {
        "total_images":   len(imgs),
        "total_feeds":    len(feeds),
        "total_rejected": rejected,
        "total_pending":  pending,
    }


@router.get("/activity")
async def activity(user=Depends(get_current_user)):
    uid = user["id"]
    items = []

    if supabase:
        imgs  = supabase.table("image_checks").select("id,safety_score,checked_at") \
                    .eq("user_id", uid).order("checked_at", desc=True).limit(5).execute().data or []
        feeds = supabase.table("feed_analyses").select("id,overall_score,analysed_at") \
                    .eq("user_id", uid).order("analysed_at", desc=True).limit(5).execute().data or []

        for i in imgs:
            items.append({"ref_type": "image", "score": i["safety_score"], "created_at": i["checked_at"]})
        for f in feeds:
            items.append({"ref_type": "feed",  "score": f["overall_score"], "created_at": f["analysed_at"]})
    else:
        for c in _LOCAL_CHECKS[-5:]:
            items.append({"ref_type": "image", "score": c["safety_score"], "created_at": c["checked_at"]})
        for f in _LOCAL_FEEDS[-5:]:
            items.append({"ref_type": "feed", "score": f["overall_score"], "created_at": f["analysed_at"]})

    items.sort(key=lambda x: x["created_at"], reverse=True)
    return {"items": items[:10]}
