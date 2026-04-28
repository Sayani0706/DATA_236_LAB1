from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.mongodb import get_db
from app.utils.auth import owner_only
from pydantic import BaseModel, field_validator
from typing import Optional
from bson import ObjectId
from datetime import datetime
import shutil, uuid

router = APIRouter()

US_STATE_ABBREVS = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC"
}


def validate_state_field(v):
    if v is None:
        return v
    v = v.strip().upper()
    if v and v not in US_STATE_ABBREVS:
        raise ValueError(f"State must be a valid 2-letter US abbreviation (e.g. CA, NY). Got: '{v}'")
    return v


class OwnerRestaurantCreate(BaseModel):
    name: str
    cuisine_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    description: Optional[str] = None
    hours: Optional[str] = None
    contact: Optional[str] = None
    pricing_tier: Optional[str] = None
    amenities: Optional[str] = None

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        return validate_state_field(v)


class OwnerRestaurantUpdate(BaseModel):
    name: Optional[str] = None
    cuisine_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    description: Optional[str] = None
    hours: Optional[str] = None
    contact: Optional[str] = None
    pricing_tier: Optional[str] = None
    amenities: Optional[str] = None

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        return validate_state_field(v)


def simple_sentiment(reviews):
    positive_words = {
        "great","amazing","excellent","fantastic","wonderful","delicious",
        "loved","love","best","awesome","perfect","outstanding","superb",
        "good","nice","tasty","fresh","friendly","recommend","incredible",
        "beautiful","clean","helpful","quick","fast","worth","enjoy",
        "enjoyed","pleasant","cozy","gorgeous","yummy","phenomenal"
    }
    negative_words = {
        "bad","terrible","awful","horrible","disgusting","worst","poor",
        "slow","cold","rude","dirty","overpriced","disappointing",
        "stale","bland","mediocre","never","avoid","waste","unpleasant",
        "unhelpful","wrong","waited","disgusted","gross","undercooked",
        "raw","sick","burned","tasteless"
    }

    positive_count = 0
    negative_count = 0
    neutral_count = 0

    for review in reviews:
        comment = (review.get("comment") or "").lower()
        rating = review.get("rating", 0)
        words = set(comment.split())
        pos_hits = len(words & positive_words)
        neg_hits = len(words & negative_words)
        if rating >= 4:
            pos_hits += 2
        elif rating <= 2:
            neg_hits += 2
        if pos_hits > neg_hits:
            positive_count += 1
        elif neg_hits > pos_hits:
            negative_count += 1
        else:
            neutral_count += 1

    total = positive_count + negative_count + neutral_count
    if total == 0:
        return {"label": "No reviews yet", "positive": 0, "neutral": 0, "negative": 0, "score": 0}
    score = round((positive_count - negative_count) / total * 100, 1)
    if score > 20:
        label = "Positive"
    elif score < -20:
        label = "Negative"
    else:
        label = "Neutral"
    return {
        "label": label,
        "positive": positive_count,
        "neutral": neutral_count,
        "negative": negative_count,
        "score": score,
    }


async def get_ratings_distribution(db, restaurant_id):
    distribution = {}
    for star in range(1, 6):
        count = await db.reviews.count_documents({
            "restaurant_id": restaurant_id,
            "rating": star
        })
        distribution[str(star)] = count
    return distribution


@router.get("/dashboard")
async def owner_dashboard(db=Depends(get_db), current_user: dict = Depends(owner_only)):
    restaurants = await db.restaurants.find({"owner_id": current_user["_id"]}).to_list(length=None)
    result = []
    for r in restaurants:
        rest_id = r["_id"]
        pipeline = [
            {"$match": {"restaurant_id": rest_id}},
            {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}, "count": {"$sum": 1}}}
        ]
        stats = await db.reviews.aggregate(pipeline).to_list(length=1)
        avg = round(stats[0]["avg_rating"], 1) if stats and stats[0]["avg_rating"] else 0
        count = stats[0]["count"] if stats else 0
        recent = await db.reviews.find({"restaurant_id": rest_id}).sort("review_date", -1).limit(5).to_list(length=None)
        all_reviews = await db.reviews.find({"restaurant_id": rest_id}).to_list(length=None)
        distribution = await get_ratings_distribution(db, rest_id)
        sentiment = simple_sentiment(all_reviews)

        recent_reviews_data = []
        for rev in recent:
            reviewer = await db.users.find_one({"_id": rev["user_id"]})
            recent_reviews_data.append({
                "id": str(rev["_id"]),
                "rating": rev["rating"],
                "comment": rev.get("comment"),
                "review_date": rev.get("review_date"),
                "user_id": str(rev["user_id"]),
                "reviewer_name": reviewer["name"] if reviewer else "Unknown",
            })

        result.append({
            "restaurant": {
                "id": str(r["_id"]),
                "name": r["name"],
                "cuisine_type": r.get("cuisine_type"),
                "city": r.get("city"),
                "state": r.get("state"),
                "pricing_tier": r.get("pricing_tier"),
                "is_claimed": r.get("is_claimed", False),
                "view_count": r.get("view_count", 0),
            },
            "avg_rating": avg,
            "review_count": count,
            "total_views": r.get("view_count", 0),
            "ratings_distribution": distribution,
            "sentiment": sentiment,
            "recent_reviews": recent_reviews_data,
        })
    return result


@router.get("/dashboard/{restaurant_id}/analytics")
async def restaurant_analytics(restaurant_id: str, db=Depends(get_db), current_user: dict = Depends(owner_only)):
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

    restaurant = await db.restaurants.find_one({"_id": rest_obj_id, "owner_id": current_user["_id"]})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found or not yours")

    all_reviews = await db.reviews.find({"restaurant_id": rest_obj_id}).to_list(length=None)
    pipeline = [
        {"$match": {"restaurant_id": rest_obj_id}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}, "count": {"$sum": 1}}}
    ]
    stats = await db.reviews.aggregate(pipeline).to_list(length=1)
    avg = round(stats[0]["avg_rating"], 1) if stats and stats[0]["avg_rating"] else 0
    count = stats[0]["count"] if stats else 0
    distribution = await get_ratings_distribution(db, rest_obj_id)
    sentiment = simple_sentiment(all_reviews)

    return {
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant["name"],
        "total_views": restaurant.get("view_count", 0),
        "avg_rating": avg,
        "total_reviews": count,
        "ratings_distribution": distribution,
        "sentiment": sentiment,
    }


@router.post("/restaurants")
async def post_restaurant(data: OwnerRestaurantCreate, db=Depends(get_db), current_user: dict = Depends(owner_only)):
    rest_doc = {
        "owner_id": current_user["_id"],
        "name": data.name,
        "cuisine_type": data.cuisine_type,
        "address": data.address,
        "city": data.city,
        "state": data.state,
        "zip": data.zip,
        "description": data.description,
        "hours": data.hours,
        "contact": data.contact,
        "pricing_tier": data.pricing_tier,
        "amenities": data.amenities,
        "is_claimed": True,
        "view_count": 0,
        "created_at": datetime.utcnow(),
        "photos": []
    }
    result = await db.restaurants.insert_one(rest_doc)
    rest_doc["id"] = str(result.inserted_id)
    return rest_doc


@router.put("/restaurants/{restaurant_id}")
async def edit_restaurant(restaurant_id: str, data: OwnerRestaurantUpdate, db=Depends(get_db), current_user: dict = Depends(owner_only)):
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

    restaurant = await db.restaurants.find_one({"_id": rest_obj_id, "owner_id": current_user["_id"]})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found or not yours")

    update_fields = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    await db.restaurants.update_one({"_id": rest_obj_id}, {"$set": update_fields})
    updated = await db.restaurants.find_one({"_id": rest_obj_id})
    updated["id"] = str(updated["_id"])
    return updated


@router.post("/restaurants/{restaurant_id}/photos")
async def upload_owner_photo(restaurant_id: str, file: UploadFile = File(...), db=Depends(get_db), current_user: dict = Depends(owner_only)):
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

    restaurant = await db.restaurants.find_one({"_id": rest_obj_id, "owner_id": current_user["_id"]})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Not found or not yours")

    ext = file.filename.split(".")[-1]
    fname = f"{uuid.uuid4()}.{ext}"
    path = f"uploads/{fname}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    await db.restaurants.update_one(
        {"_id": rest_obj_id},
        {"$push": {"photos": {"photo_url": f"/{path}", "uploaded_at": datetime.utcnow()}}}
    )
    return {"photo_url": f"/{path}"}


@router.get("/restaurants")
async def get_my_restaurants(db=Depends(get_db), current_user: dict = Depends(owner_only)):
    restaurants = await db.restaurants.find({"owner_id": current_user["_id"]}).to_list(length=None)
    result = []
    for r in restaurants:
        rest_id = r["_id"]
        pipeline = [
            {"$match": {"restaurant_id": rest_id}},
            {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}, "count": {"$sum": 1}}}
        ]
        stats = await db.reviews.aggregate(pipeline).to_list(length=1)
        avg = round(stats[0]["avg_rating"], 1) if stats and stats[0]["avg_rating"] else 0
        count = stats[0]["count"] if stats else 0
        photos = [{"id": str(i), "photo_url": p["photo_url"]} for i, p in enumerate(r.get("photos", []))]
        result.append({
            "id": str(r["_id"]),
            "name": r["name"],
            "cuisine_type": r.get("cuisine_type"),
            "address": r.get("address"),
            "city": r.get("city"),
            "state": r.get("state"),
            "zip": r.get("zip"),
            "description": r.get("description"),
            "hours": r.get("hours"),
            "contact": r.get("contact"),
            "pricing_tier": r.get("pricing_tier"),
            "amenities": r.get("amenities"),
            "is_claimed": r.get("is_claimed", False),
            "view_count": r.get("view_count", 0),
            "avg_rating": avg,
            "review_count": count,
            "photos": photos,
        })
    return result


@router.get("/restaurants/{restaurant_id}/reviews")
async def get_restaurant_reviews(restaurant_id: str, db=Depends(get_db), current_user: dict = Depends(owner_only)):
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

    restaurant = await db.restaurants.find_one({"_id": rest_obj_id, "owner_id": current_user["_id"]})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found or not yours")

    reviews = await db.reviews.find({"restaurant_id": rest_obj_id}).sort("review_date", -1).to_list(length=None)
    result = []
    for rev in reviews:
        reviewer = await db.users.find_one({"_id": rev["user_id"]})
        result.append({
            "id": str(rev["_id"]),
            "rating": rev["rating"],
            "comment": rev.get("comment"),
            "review_date": rev.get("review_date"),
            "updated_at": rev.get("updated_at"),
            "user_id": str(rev["user_id"]),
            "reviewer_name": reviewer["name"] if reviewer else "Unknown",
            "reviewer_photo": reviewer.get("profile_picture") if reviewer else None,
        })
    return result
