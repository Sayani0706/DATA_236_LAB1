from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.restaurant import Restaurant, RestaurantPhoto
from app.models.review import Review
from app.models.user import User
from app.models.preferences import UserPreference
from app.utils.auth import get_current_user
from pydantic import BaseModel, field_validator
from typing import Optional
import shutil, uuid

router = APIRouter()

# ── Shared state validation 
US_STATE_ABBREVS = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC"
}

def validate_state_field(v):
    """Reusable state validator — call from field_validator in each schema."""
    if v is None:
        return v
    v = v.strip().upper()
    if v and v not in US_STATE_ABBREVS:
        raise ValueError(
            f"State must be a valid 2-letter US abbreviation (e.g. CA, NY). Got: '{v}'"
        )
    return v


# ── Schemas
class RestaurantCreate(BaseModel):
    name: str
    cuisine_type: Optional[str] = None
    address:      Optional[str] = None
    city:         Optional[str] = None
    state:        Optional[str] = None
    zip:          Optional[str] = None
    description:  Optional[str] = None
    hours:        Optional[str] = None
    contact:      Optional[str] = None
    pricing_tier: Optional[str] = None
    amenities:    Optional[str] = None

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        return validate_state_field(v)


class RestaurantUpdate(BaseModel):
    name:         Optional[str] = None
    cuisine_type: Optional[str] = None
    address:      Optional[str] = None
    city:         Optional[str] = None
    state:        Optional[str] = None
    zip:          Optional[str] = None
    description:  Optional[str] = None
    hours:        Optional[str] = None
    contact:      Optional[str] = None
    pricing_tier: Optional[str] = None
    amenities:    Optional[str] = None

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        return validate_state_field(v)


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.get("/")
def search_restaurants(
    name:     Optional[str] = Query(None),
    cuisine:  Optional[str] = Query(None),
    keyword:  Optional[str] = Query(None),
    city:     Optional[str] = Query(None),
    zip:      Optional[str] = Query(None),
    sort_by:  Optional[str] = Query(None),
    skip:     int           = Query(0,  ge=0),
    limit:    int           = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(Restaurant)
    if name:
        q = q.filter(Restaurant.name.ilike(f"%{name}%"))
    if cuisine:
        q = q.filter(Restaurant.cuisine_type.ilike(f"%{cuisine}%"))
    if keyword:
        q = q.filter(
            Restaurant.description.ilike(f"%{keyword}%") |
            Restaurant.amenities.ilike(f"%{keyword}%")
        )
    if city:
        q = q.filter(Restaurant.city.ilike(f"%{city}%"))
    if zip:
        q = q.filter(Restaurant.zip == zip)

    restaurants = q.offset(skip).limit(limit).all()

    result = []
    for r in restaurants:
        avg   = db.query(func.avg(Review.rating)).filter(Review.restaurant_id == r.id).scalar()
        count = db.query(func.count(Review.id)).filter(Review.restaurant_id == r.id).scalar()
        result.append({
            "restaurant":   r,
            "avg_rating":   round(float(avg), 1) if avg else 0,
            "review_count": count,
        })

    if sort_by == "rating":
        result.sort(key=lambda x: x["avg_rating"], reverse=True)
    elif sort_by == "popularity":
        result.sort(key=lambda x: x["review_count"], reverse=True)
    elif sort_by == "price":
        result.sort(key=lambda x: len(x["restaurant"].pricing_tier or ""))

    return result


@router.get("/search-with-prefs")
def search_with_preferences(
    name:    Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    city:    Optional[str] = Query(None),
    zip:     Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    skip:    int            = Query(0,  ge=0),
    limit:   int            = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()

    if not city    and prefs and prefs.location:
        city    = prefs.location.split(",")[0].strip()
    if not cuisine and prefs and prefs.cuisines:
        cuisine = prefs.cuisines.split(",")[0].strip()
    if not sort_by and prefs and prefs.sort_preference:
        sort_by = prefs.sort_preference

    q = db.query(Restaurant)
    if name:
        q = q.filter(Restaurant.name.ilike(f"%{name}%"))
    if cuisine:
        q = q.filter(Restaurant.cuisine_type.ilike(f"%{cuisine}%"))
    if keyword:
        q = q.filter(
            Restaurant.description.ilike(f"%{keyword}%") |
            Restaurant.amenities.ilike(f"%{keyword}%")
        )
    if city:
        q = q.filter(Restaurant.city.ilike(f"%{city}%"))
    if zip:
        q = q.filter(Restaurant.zip == zip)
    if prefs and prefs.dietary_needs and prefs.dietary_needs != "none":
        q = q.filter(Restaurant.amenities.ilike(f"%{prefs.dietary_needs}%"))

    restaurants = q.offset(skip).limit(limit).all()

    result = []
    for r in restaurants:
        avg   = db.query(func.avg(Review.rating)).filter(Review.restaurant_id == r.id).scalar()
        count = db.query(func.count(Review.id)).filter(Review.restaurant_id == r.id).scalar()
        result.append({
            "restaurant":   r,
            "avg_rating":   round(float(avg), 1) if avg else 0,
            "review_count": count,
        })

    if sort_by == "rating":
        result.sort(key=lambda x: x["avg_rating"], reverse=True)
    elif sort_by == "popularity":
        result.sort(key=lambda x: x["review_count"], reverse=True)
    elif sort_by == "price":
        result.sort(key=lambda x: len(x["restaurant"].pricing_tier or ""))

    return result


@router.get("/{restaurant_id}")
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Increment view count every time the detail page is fetched
    r.view_count = (r.view_count or 0) + 1
    db.commit()

    avg   = db.query(func.avg(Review.rating)).filter(Review.restaurant_id == restaurant_id).scalar()
    count = db.query(func.count(Review.id)).filter(Review.restaurant_id == restaurant_id).scalar()

    restaurant_photos = [
        {"id": p.id, "photo_url": p.photo_url}
        for p in r.photos
    ]

    reviews_with_user = []
    for review in r.reviews:
        reviewer = db.query(User).filter(User.id == review.user_id).first()
        reviews_with_user.append({
            "id":            review.id,
            "rating":        review.rating,
            "comment":       review.comment,
            "review_date":   review.review_date,
            "updated_at":    review.updated_at,
            "user_id":       review.user_id,
            "reviewer_name": reviewer.name if reviewer else "Unknown",
            "reviewer_photo": reviewer.profile_picture if reviewer else None,
            "photos": [
                {"id": p.id, "photo_url": p.photo_url}
                for p in review.photos
            ],
        })

    return {
        "restaurant": {
            "id":           r.id,
            "name":         r.name,
            "cuisine_type": r.cuisine_type,
            "address":      r.address,
            "city":         r.city,
            "state":        r.state,
            "zip":          r.zip,
            "description":  r.description,
            "hours":        r.hours,
            "contact":      r.contact,
            "pricing_tier": r.pricing_tier,
            "amenities":    r.amenities,
            "is_claimed":   r.is_claimed,
            "view_count":   r.view_count or 0,
            "photos":       restaurant_photos,
        },
        "avg_rating":   round(float(avg), 1) if avg else 0,
        "review_count": count,
        "reviews":      reviews_with_user,
    }


@router.get("/{restaurant_id}/ratings-distribution")
def get_ratings_distribution(restaurant_id: int, db: Session = Depends(get_db)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    distribution = {}
    for star in range(1, 6):
        count = db.query(func.count(Review.id)).filter(
            Review.restaurant_id == restaurant_id,
            Review.rating == star
        ).scalar()
        distribution[str(star)] = count or 0
    total = sum(distribution.values())
    return {
        "restaurant_id": restaurant_id,
        "distribution":  distribution,
        "total_reviews": total,
    }


@router.post("/")
def create_restaurant(
    data: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    r = Restaurant(**data.dict(), owner_id=current_user.id)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.put("/{restaurant_id}")
def update_restaurant(
    restaurant_id: int,
    data: RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    if r.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for k, v in data.dict(exclude_none=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.post("/{restaurant_id}/photos")
def upload_restaurant_photo(
    restaurant_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    ext   = file.filename.split(".")[-1]
    fname = f"{uuid.uuid4()}.{ext}"
    path  = f"uploads/{fname}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    photo = RestaurantPhoto(restaurant_id=restaurant_id, photo_url=f"/{path}")
    db.add(photo)
    db.commit()
    return {"photo_url": photo.photo_url}


@router.post("/{restaurant_id}/claim")
def claim_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only owners can claim restaurants")
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    if r.is_claimed:
        raise HTTPException(status_code=400, detail="Already claimed")
    r.owner_id  = current_user.id
    r.is_claimed = True
    db.commit()
    return {"message": "Restaurant claimed successfully"}
