from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.restaurant import Restaurant, RestaurantPhoto
from app.models.review import Review
from app.utils.auth import get_current_user, owner_only
from app.models.user import User
from pydantic import BaseModel
from typing import Optional
import shutil, uuid

router = APIRouter()

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

@router.get("/dashboard")
def owner_dashboard(db: Session = Depends(get_db), current_user: User = Depends(owner_only)):
    restaurants = db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).all()
    result = []
    for r in restaurants:
        avg = db.query(func.avg(Review.rating)).filter(Review.restaurant_id == r.id).scalar()
        count = db.query(func.count(Review.id)).filter(Review.restaurant_id == r.id).scalar()
        recent = db.query(Review).filter(Review.restaurant_id == r.id).order_by(Review.review_date.desc()).limit(5).all()
        result.append({
            "restaurant": r,
            "avg_rating": round(float(avg), 1) if avg else 0,
            "review_count": count,
            "recent_reviews": recent
        })
    return result

@router.post("/restaurants")
def post_restaurant(data: OwnerRestaurantCreate, db: Session = Depends(get_db), current_user: User = Depends(owner_only)):
    r = Restaurant(**data.dict(), owner_id=current_user.id, is_claimed=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.put("/restaurants/{restaurant_id}")
def edit_restaurant(restaurant_id: int, data: OwnerRestaurantUpdate, db: Session = Depends(get_db), current_user: User = Depends(owner_only)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id, Restaurant.owner_id == current_user.id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found or not yours")
    for k, v in data.dict(exclude_none=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r

@router.post("/restaurants/{restaurant_id}/photos")
def upload_owner_photo(restaurant_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(owner_only)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id, Restaurant.owner_id == current_user.id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found or not yours")
    ext = file.filename.split(".")[-1]
    fname = f"{uuid.uuid4()}.{ext}"
    path = f"uploads/{fname}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    photo = RestaurantPhoto(restaurant_id=restaurant_id, photo_url=f"/{path}")
    db.add(photo)
    db.commit()
    return {"photo_url": photo.photo_url}

@router.get("/restaurants/{restaurant_id}/reviews")
def get_restaurant_reviews(restaurant_id: int, db: Session = Depends(get_db), current_user: User = Depends(owner_only)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id, Restaurant.owner_id == current_user.id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found or not yours")
    return db.query(Review).filter(Review.restaurant_id == restaurant_id).all()
