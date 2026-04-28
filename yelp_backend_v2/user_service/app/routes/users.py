from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.mongodb import get_db
from app.utils.auth import get_current_user
from app.kafka_producer import publish_event
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import shutil, uuid
from datetime import datetime

router = APIRouter()

US_STATE_ABBREVS = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC"
}


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    about_me: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    languages: Optional[str] = None
    gender: Optional[str] = None

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        if v is None:
            return v
        v = v.strip().upper()
        if v and v not in US_STATE_ABBREVS:
            raise ValueError(f"State must be a valid 2-letter US abbreviation (e.g. CA, NY). Got: '{v}'")
        return v


class PreferencesUpdate(BaseModel):
    cuisines: Optional[str] = None
    price_range: Optional[str] = None
    location: Optional[str] = None
    search_radius: Optional[int] = None
    dietary_needs: Optional[str] = None
    ambiance: Optional[str] = None
    sort_preference: Optional[str] = None


def safe_user(user):
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "phone": user.get("phone"),
        "about_me": user.get("about_me"),
        "city": user.get("city"),
        "state": user.get("state"),
        "country": user.get("country"),
        "languages": user.get("languages"),
        "gender": user.get("gender"),
        "profile_picture": user.get("profile_picture"),
        "created_at": user.get("created_at")
    }


@router.get("/me")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return safe_user(current_user)


@router.put("/me")
async def update_profile(data: ProfileUpdate, db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if data.email and data.email != current_user["email"]:
        existing = await db.users.find_one({"email": data.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")

    update_data = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    await db.users.update_one({"_id": current_user["_id"]}, {"$set": update_data})
    updated_user = await db.users.find_one({"_id": current_user["_id"]})
    event = {
        "user_id": str(current_user["_id"]),
        "updated_fields": update_data,
        "updated_at": datetime.utcnow().isoformat(),
    }
    try:
        await publish_event("user.updated", event)
    except Exception:
        raise HTTPException(status_code=503, detail="Failed to queue user update event")
    return safe_user(updated_user)


@router.post("/me/photo")
async def upload_photo(file: UploadFile = File(...), db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    ext = file.filename.split(".")[-1]
    fname = f"{uuid.uuid4()}.{ext}"
    path = f"uploads/{fname}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"profile_picture": f"/{path}"}}
    )
    return {"profile_picture": f"/{path}"}


@router.get("/me/preferences")
async def get_preferences(db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    prefs = current_user.get("preferences", {})
    if not prefs or not any(prefs.values()):
        raise HTTPException(status_code=404, detail="No preferences set")
    return prefs


@router.put("/me/preferences")
async def update_preferences(data: PreferencesUpdate, db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    prefs_update = {f"preferences.{k}": v for k, v in data.model_dump(exclude_none=True).items()}
    await db.users.update_one({"_id": current_user["_id"]}, {"$set": prefs_update})
    updated_user = await db.users.find_one({"_id": current_user["_id"]})
    event = {
        "user_id": str(current_user["_id"]),
        "updated_fields": {"preferences": updated_user.get("preferences", {})},
        "updated_at": datetime.utcnow().isoformat(),
    }
    try:
        await publish_event("user.updated", event)
    except Exception:
        raise HTTPException(status_code=503, detail="Failed to queue user update event")
    return updated_user.get("preferences", {})


@router.get("/me/history")
async def get_history(db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    reviews = await db.reviews.find({"user_id": current_user["_id"]}).to_list(length=None)
    restaurants = await db.restaurants.find({"owner_id": current_user["_id"]}).to_list(length=None)

    reviews_with_restaurant = []
    for rev in reviews:
        restaurant = await db.restaurants.find_one({"_id": rev["restaurant_id"]})
        reviews_with_restaurant.append({
            "id": str(rev["_id"]),
            "restaurant_id": str(rev["restaurant_id"]),
            "restaurant_name": restaurant["name"] if restaurant else "Unknown",
            "rating": rev["rating"],
            "comment": rev.get("comment"),
            "review_date": rev.get("review_date"),
            "updated_at": rev.get("updated_at")
        })

    return {
        "reviews": reviews_with_restaurant,
        "restaurants_added": [
            {
                "id": str(r["_id"]),
                "name": r["name"],
                "cuisine_type": r.get("cuisine_type"),
                "city": r.get("city"),
                "created_at": r.get("created_at")
            }
            for r in restaurants
        ]
    }
