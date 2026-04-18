from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.favorite import Favorite
from app.models.restaurant import Restaurant
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/{restaurant_id}")
def add_favorite(restaurant_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    existing = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.restaurant_id == restaurant_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")
    fav = Favorite(user_id=current_user.id, restaurant_id=restaurant_id)
    db.add(fav)
    db.commit()
    return {"message": "Added to favorites"}

@router.delete("/{restaurant_id}")
def remove_favorite(restaurant_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fav = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.restaurant_id == restaurant_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Not in favorites")
    db.delete(fav)
    db.commit()
    return {"message": "Removed from favorites"}

@router.get("/")
def get_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from sqlalchemy import func
    from app.models.review import Review
    
    favs = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    result = []
    for f in favs:
        r = f.restaurant
        avg = db.query(func.avg(Review.rating)).filter(Review.restaurant_id == r.id).scalar()
        count = db.query(func.count(Review.id)).filter(Review.restaurant_id == r.id).scalar()
        result.append({
            "id": r.id,
            "name": r.name,
            "cuisine_type": r.cuisine_type,
            "address": r.address,
            "city": r.city,
            "state": r.state,
            "pricing_tier": r.pricing_tier,
            "description": r.description,
            "avg_rating": round(float(avg), 1) if avg else 0,
            "review_count": count or 0
        })
    return result
