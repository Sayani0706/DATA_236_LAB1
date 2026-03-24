from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.review import Review, ReviewPhoto
from app.models.restaurant import Restaurant
from app.utils.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import Optional
import shutil, uuid

router = APIRouter()

class ReviewCreate(BaseModel):
    restaurant_id: int
    rating: int
    comment: Optional[str] = None

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

@router.post("/")
def create_review(data: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not 1 <= data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    r = db.query(Restaurant).filter(Restaurant.id == data.restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    review = Review(user_id=current_user.id, restaurant_id=data.restaurant_id, rating=data.rating, comment=data.comment)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@router.get("/restaurant/{restaurant_id}")
def get_reviews(restaurant_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.restaurant_id == restaurant_id).all()

@router.put("/{review_id}")
def update_review(review_id: int, data: ReviewUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if data.rating and not 1 <= data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    for k, v in data.dict(exclude_none=True).items():
        setattr(review, k, v)
    db.commit()
    db.refresh(review)
    return review

@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(review)
    db.commit()
    return {"message": "Review deleted"}

@router.post("/{review_id}/photos")
def upload_review_photo(review_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review or review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    ext = file.filename.split(".")[-1]
    fname = f"{uuid.uuid4()}.{ext}"
    path = f"uploads/{fname}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    photo = ReviewPhoto(review_id=review_id, photo_url=f"/{path}")
    db.add(photo)
    db.commit()
    return {"photo_url": photo.photo_url}
