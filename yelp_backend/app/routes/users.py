from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.preferences import UserPreference
from app.models.review import Review
from app.models.restaurant import Restaurant
from app.utils.auth import get_current_user
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import shutil, os, uuid

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
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "phone": user.phone,
        "about_me": user.about_me,
        "city": user.city,
        "state": user.state,
        "country": user.country,
        "languages": user.languages,
        "gender": user.gender,
        "profile_picture": user.profile_picture,
        "created_at": user.created_at
    }

@router.get("/me")
def get_profile(current_user: User = Depends(get_current_user)):
    return safe_user(current_user)

@router.put("/me")
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if data.email and data.email != current_user.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
    for k, v in data.dict(exclude_none=True).items():
        setattr(current_user, k, v)
    db.commit()
    db.refresh(current_user)
    return safe_user(current_user)

@router.post("/me/photo")
def upload_photo(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ext = file.filename.split(".")[-1]
    fname = f"{uuid.uuid4()}.{ext}"
    path = f"uploads/{fname}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    current_user.profile_picture = f"/{path}"
    db.commit()
    return {"profile_picture": current_user.profile_picture}

@router.get("/me/preferences")
def get_preferences(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="No preferences set")
    return prefs

@router.put("/me/preferences")
def update_preferences(data: PreferencesUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not prefs:
        prefs = UserPreference(user_id=current_user.id)
        db.add(prefs)
    for k, v in data.dict(exclude_none=True).items():
        setattr(prefs, k, v)
    db.commit()
    db.refresh(prefs)
    return prefs

@router.get("/me/history")
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.restaurant import Restaurant
    
    reviews = db.query(Review).filter(Review.user_id == current_user.id).all()
    restaurants = db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).all()

    reviews_with_restaurant = []
    for rev in reviews:
        restaurant = db.query(Restaurant).filter(Restaurant.id == rev.restaurant_id).first()
        reviews_with_restaurant.append({
            "id": rev.id,
            "restaurant_id": rev.restaurant_id,
            "restaurant_name": restaurant.name if restaurant else "Unknown",
            "rating": rev.rating,
            "comment": rev.comment,
            "review_date": rev.review_date,
            "updated_at": rev.updated_at
        })

    return {
        "reviews": reviews_with_restaurant,
        "restaurants_added": restaurants
    }