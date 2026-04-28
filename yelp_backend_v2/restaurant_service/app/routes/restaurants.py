from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from app.mongodb import get_db
from app.utils.auth import get_current_user
from pydantic import BaseModel, field_validator
from typing import Optional
from bson import ObjectId
from datetime import datetime
import shutil, uuid
from app.kafka_producer import publish_event

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


class RestaurantCreate(BaseModel):
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


class RestaurantUpdate(BaseModel):
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


async def calculate_avg_rating(db, restaurant_id):
    pipeline = [
        {"$match": {"restaurant_id": restaurant_id}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}, "count": {"$sum": 1}}}
    ]
    result = await db.reviews.aggregate(pipeline).to_list(length=1)
    if result:
        return round(result[0]["avg_rating"], 1), result[0]["count"]
    return 0, 0


@router.get("/")
async def search_restaurants(
    name: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    zip: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db)
):
    query_filter = {}
    if name:
        query_filter["name"] = {"$regex": name, "$options": "i"}
    if cuisine:
        query_filter["cuisine_type"] = {"$regex": cuisine, "$options": "i"}
    if keyword:
        query_filter["$or"] = [
            {"description": {"$regex": keyword, "$options": "i"}},
            {"amenities": {"$regex": keyword, "$options": "i"}}
        ]
    if city:
        query_filter["city"] = {"$regex": city, "$options": "i"}
    if zip:
        query_filter["zip"] = zip

    restaurants = await db.restaurants.find(query_filter).skip(skip).limit(limit).to_list(length=None)
    result = []
    for r in restaurants:
        avg, count = await calculate_avg_rating(db, r["_id"])
        result.append({
            "restaurant": {
                "id": str(r["_id"]),
                "name": r["name"],
                "cuisine_type": r.get("cuisine_type"),
                "city": r.get("city"),
                "state": r.get("state"),
                "pricing_tier": r.get("pricing_tier"),
                "description": r.get("description")
            },
            "avg_rating": avg,
            "review_count": count,
        })

    if sort_by == "rating":
        result.sort(key=lambda x: x["avg_rating"], reverse=True)
    elif sort_by == "popularity":
        result.sort(key=lambda x: x["review_count"], reverse=True)
    elif sort_by == "price":
        result.sort(key=lambda x: len(x["restaurant"].get("pricing_tier") or ""))
    return result


@router.get("/search-with-prefs")
async def search_with_preferences(
    name: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    zip: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    prefs = current_user.get("preferences", {})
    if not city and prefs.get("location"):
        city = prefs["location"].split(",")[0].strip()
    if not cuisine and prefs.get("cuisines"):
        cuisine = prefs["cuisines"].split(",")[0].strip()
    if not sort_by and prefs.get("sort_preference"):
        sort_by = prefs["sort_preference"]

    query_filter = {}
    if name:
        query_filter["name"] = {"$regex": name, "$options": "i"}
    if cuisine:
        query_filter["cuisine_type"] = {"$regex": cuisine, "$options": "i"}
    if keyword:
        query_filter["$or"] = [
            {"description": {"$regex": keyword, "$options": "i"}},
            {"amenities": {"$regex": keyword, "$options": "i"}}
        ]
    if city:
        query_filter["city"] = {"$regex": city, "$options": "i"}
    if zip:
        query_filter["zip"] = zip
    if prefs.get("dietary_needs") and prefs["dietary_needs"] != "none":
        query_filter["amenities"] = {"$regex": prefs["dietary_needs"], "$options": "i"}

    restaurants = await db.restaurants.find(query_filter).skip(skip).limit(limit).to_list(length=None)
    result = []
    for r in restaurants:
        avg, count = await calculate_avg_rating(db, r["_id"])
        result.append({
            "restaurant": {
                "id": str(r["_id"]),
                "name": r["name"],
                "cuisine_type": r.get("cuisine_type"),
                "city": r.get("city"),
                "state": r.get("state"),
                "pricing_tier": r.get("pricing_tier"),
                "description": r.get("description")
            },
            "avg_rating": avg,
            "review_count": count,
        })
    if sort_by == "rating":
        result.sort(key=lambda x: x["avg_rating"], reverse=True)
    elif sort_by == "popularity":
        result.sort(key=lambda x: x["review_count"], reverse=True)
    elif sort_by == "price":
        result.sort(key=lambda x: len(x["restaurant"].get("pricing_tier") or ""))
    return result


@router.get("/{restaurant_id}")
async def get_restaurant(restaurant_id: str, db=Depends(get_db)):
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

    r = await db.restaurants.find_one({"_id": rest_obj_id})
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    await db.restaurants.update_one({"_id": rest_obj_id}, {"$inc": {"view_count": 1}})
    avg, count = await calculate_avg_rating(db, rest_obj_id)
    restaurant_photos = [{"id": str(i), "photo_url": p["photo_url"]} for i, p in enumerate(r.get("photos", []))]
    reviews = await db.reviews.find({"restaurant_id": rest_obj_id}).to_list(length=None)

    reviews_with_user = []
    for review in reviews:
        reviewer = await db.users.find_one({"_id": review["user_id"]})
        reviews_with_user.append({
            "id": str(review["_id"]),
            "rating": review["rating"],
            "comment": review.get("comment"),
            "review_date": review.get("review_date"),
            "updated_at": review.get("updated_at"),
            "user_id": str(review["user_id"]),
            "reviewer_name": reviewer["name"] if reviewer else "Unknown",
            "reviewer_photo": reviewer.get("profile_picture") if reviewer else None,
            "photos": review.get("photos", [])
        })

    return {
        "restaurant": {
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
            "photos": restaurant_photos,
        },
        "avg_rating": avg,
        "review_count": count,
        "reviews": reviews_with_user,
    }


@router.get("/{restaurant_id}/ratings-distribution")
async def get_ratings_distribution(restaurant_id: str, db=Depends(get_db)):
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")
    r = await db.restaurants.find_one({"_id": rest_obj_id})
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    distribution = {}
    for star in range(1, 6):
        count = await db.reviews.count_documents({"restaurant_id": rest_obj_id, "rating": star})
        distribution[str(star)] = count
    total = sum(distribution.values())
    return {"restaurant_id": restaurant_id, "distribution": distribution, "total_reviews": total}


@router.post("/")
async def create_restaurant(data: RestaurantCreate, db=Depends(get_db), current_user: dict = Depends(get_current_user)):
    restaurant_id = str(ObjectId())
    event = {
        "restaurant_id": restaurant_id,
        "owner_id": str(current_user["_id"]),
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
        "is_claimed": False,
        "view_count": 0,
        "created_at": datetime.utcnow().isoformat(),
        "photos": []
    }
    try:
        await publish_event("restaurant.created", event)
    except Exception:
        raise HTTPException(status_code=503, detail="Failed to queue restaurant event")

    return {
        "id": restaurant_id,
        "owner_id": str(current_user["_id"]),
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
        "is_claimed": False,
        "view_count": 0,
        "photos": [],
        "status": "queued"
    }


@router.put("/{restaurant_id}")
async def update_restaurant(restaurant_id: str, data: RestaurantUpdate, db=Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")
    restaurant = await db.restaurants.find_one({"_id": rest_obj_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Not found")
    if restaurant.get("owner_id") != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_fields = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    await db.restaurants.update_one({"_id": rest_obj_id}, {"$set": update_fields})
    updated = await db.restaurants.find_one({"_id": rest_obj_id})
    updated["id"] = str(updated["_id"])
    return updated


@router.post("/{restaurant_id}/photos")
async def upload_restaurant_photo(restaurant_id: str, file: UploadFile = File(...), db=Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")
    restaurant = await db.restaurants.find_one({"_id": rest_obj_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Not found")

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


@router.post("/{restaurant_id}/claim")
async def claim_restaurant(restaurant_id: str, db=Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Only owners can claim restaurants")
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")
    restaurant = await db.restaurants.find_one({"_id": rest_obj_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Not found")
    if restaurant.get("is_claimed"):
        raise HTTPException(status_code=400, detail="Already claimed")

    await db.restaurants.update_one(
        {"_id": rest_obj_id},
        {"$set": {"owner_id": current_user["_id"], "is_claimed": True}}
    )
    return {"message": "Restaurant claimed successfully"}
