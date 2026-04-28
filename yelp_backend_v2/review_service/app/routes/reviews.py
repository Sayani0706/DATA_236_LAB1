from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.mongodb import get_db
from app.utils.auth import get_current_user
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from datetime import datetime
import shutil, uuid
from app.kafka_producer import publish_event

router = APIRouter()


class ReviewCreate(BaseModel):
    restaurant_id: str
    rating: int
    comment: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None


@router.post("/")
async def create_review(data: ReviewCreate, db=Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not 1 <= data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    try:
        rest_obj_id = ObjectId(data.restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

    restaurant = await db.restaurants.find_one({"_id": rest_obj_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    existing = await db.reviews.find_one({
        "user_id": current_user["_id"],
        "restaurant_id": rest_obj_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this restaurant. Edit your existing review instead.")

    review_id = str(ObjectId())
    now = datetime.utcnow().isoformat()
    event = {
        "review_id": review_id,
        "user_id": str(current_user["_id"]),
        "restaurant_id": str(rest_obj_id),
        "rating": data.rating,
        "comment": data.comment,
        "review_date": now,
        "updated_at": now
    }
    try:
        await publish_event("review.created", event)
    except Exception:
        raise HTTPException(status_code=503, detail="Failed to queue review event")

    return {
        "id": review_id,
        "status": "queued",
        "message": "Review create event published"
    }


@router.get("/restaurant/{restaurant_id}")
async def get_reviews(restaurant_id: str, db=Depends(get_db)):
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

    reviews = await db.reviews.find({"restaurant_id": rest_obj_id}).to_list(length=None)
    return [
        {
            "id": str(r["_id"]),
            "user_id": str(r["user_id"]),
            "restaurant_id": str(r["restaurant_id"]),
            "rating": r["rating"],
            "comment": r.get("comment"),
            "review_date": r.get("review_date"),
            "updated_at": r.get("updated_at"),
            "photos": r.get("photos", [])
        }
        for r in reviews
    ]


@router.put("/{review_id}")
async def update_review(review_id: str, data: ReviewUpdate, db=Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        review_obj_id = ObjectId(review_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid review ID")

    review = await db.reviews.find_one({"_id": review_obj_id})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    if data.rating and not 1 <= data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    update_fields = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    update_fields["updated_at"] = datetime.utcnow().isoformat()
    event = {
        "review_id": review_id,
        "user_id": str(current_user["_id"]),
        **update_fields
    }
    try:
        await publish_event("review.updated", event)
    except Exception:
        raise HTTPException(status_code=503, detail="Failed to queue review event")

    return {
        "id": review_id,
        "status": "queued",
        "message": "Review update event published"
    }


@router.delete("/{review_id}")
async def delete_review(review_id: str, db=Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        review_obj_id = ObjectId(review_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid review ID")

    review = await db.reviews.find_one({"_id": review_obj_id})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    event = {
        "review_id": review_id,
        "user_id": str(current_user["_id"]),
        "deleted_at": datetime.utcnow().isoformat()
    }
    try:
        await publish_event("review.deleted", event)
    except Exception:
        raise HTTPException(status_code=503, detail="Failed to queue review event")
    return {"status": "queued", "message": "Review delete event published"}


@router.post("/{review_id}/photos")
async def upload_review_photo(review_id: str, file: UploadFile = File(...), db=Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        review_obj_id = ObjectId(review_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid review ID")

    review = await db.reviews.find_one({"_id": review_obj_id})
    if not review or review["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    original_name = file.filename or "upload"
    ext = original_name.split(".")[-1]
    fname = f"{uuid.uuid4()}.{ext}"
    path = f"uploads/{fname}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    await db.reviews.update_one(
        {"_id": review_obj_id},
        {"$push": {"photos": {"photo_url": f"/{path}"}}}
    )
    return {"photo_url": f"/{path}"}
