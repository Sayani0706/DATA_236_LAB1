from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.restaurant import Restaurant, RestaurantPhoto
from app.models.review import Review
from app.utils.auth import get_current_user, owner_only
from app.models.user import User
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
    if v is None:
        return v
    v = v.strip().upper()
    if v and v not in US_STATE_ABBREVS:
        raise ValueError(
            f"State must be a valid 2-letter US abbreviation (e.g. CA, NY). Got: '{v}'"
        )
    return v


# ── Schemas 

class OwnerRestaurantCreate(BaseModel):
    name:         str
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


class OwnerRestaurantUpdate(BaseModel):
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


# ── Sentiment helpers 
def simple_sentiment(reviews):
    """
    Rule-based sentiment analysis on review comments + ratings.
    Returns overall label and per-category counts.
    """
    POSITIVE_WORDS = {
        "great","amazing","excellent","fantastic","wonderful","delicious",
        "loved","love","best","awesome","perfect","outstanding","superb",
        "good","nice","tasty","fresh","friendly","recommend","incredible",
        "beautiful","clean","helpful","quick","fast","worth","enjoy",
        "enjoyed","pleasant","cozy","gorgeous","yummy","phenomenal"
    }
    NEGATIVE_WORDS = {
        "bad","terrible","awful","horrible","disgusting","worst","poor",
        "slow","cold","rude","dirty","overpriced","disappointing",
        "stale","bland","mediocre","never","avoid","waste","unpleasant",
        "unhelpful","wrong","waited","disgusted","gross","undercooked",
        "raw","sick","burned","tasteless"
    }

    positive_count = 0
    negative_count = 0
    neutral_count  = 0

    for review in reviews:
        comment  = (review.comment or "").lower()
        rating   = review.rating or 0
        words    = set(comment.split())
        pos_hits = len(words & POSITIVE_WORDS)
        neg_hits = len(words & NEGATIVE_WORDS)

        # Weight rating score heavily
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
        "label":    label,
        "positive": positive_count,
        "neutral":  neutral_count,
        "negative": negative_count,
        "score":    score,
    }


def get_ratings_distribution(db, restaurant_id):
    distribution = {}
    for star in range(1, 6):
        count = db.query(func.count(Review.id)).filter(
            Review.restaurant_id == restaurant_id,
            Review.rating == star
        ).scalar()
        distribution[str(star)] = count or 0
    return distribution


# ── Routes 

@router.get("/dashboard")
def owner_dashboard(db: Session = Depends(get_db), current_user: User = Depends(owner_only)):
    restaurants = db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).all()
    result = []
    for r in restaurants:
        avg         = db.query(func.avg(Review.rating)).filter(Review.restaurant_id == r.id).scalar()
        count       = db.query(func.count(Review.id)).filter(Review.restaurant_id == r.id).scalar()
        recent      = db.query(Review).filter(Review.restaurant_id == r.id).order_by(Review.review_date.desc()).limit(5).all()
        all_reviews = db.query(Review).filter(Review.restaurant_id == r.id).all()

        distribution = get_ratings_distribution(db, r.id)
        sentiment    = simple_sentiment(all_reviews)

        result.append({
            "restaurant": {
                "id":           r.id,
                "name":         r.name,
                "cuisine_type": r.cuisine_type,
                "city":         r.city,
                "state":        r.state,
                "pricing_tier": r.pricing_tier,
                "is_claimed":   r.is_claimed,
                "view_count":   r.view_count or 0,
            },
            "avg_rating":          round(float(avg), 1) if avg else 0,
            "review_count":        count or 0,
            "total_views":         r.view_count or 0,
            "ratings_distribution": distribution,
            "sentiment":           sentiment,
            "recent_reviews": [
                {
                    "id":            rev.id,
                    "rating":        rev.rating,
                    "comment":       rev.comment,
                    "review_date":   rev.review_date,
                    "user_id":       rev.user_id,
                    "reviewer_name": (lambda u: u.name if u else "Unknown")(
                        db.query(User).filter(User.id == rev.user_id).first()
                    ),
                }
                for rev in recent
            ],
        })
    return result


@router.get("/dashboard/{restaurant_id}/analytics")
def restaurant_analytics(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(owner_only)
):
    r = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found or not yours")

    all_reviews  = db.query(Review).filter(Review.restaurant_id == restaurant_id).all()
    avg          = db.query(func.avg(Review.rating)).filter(Review.restaurant_id == restaurant_id).scalar()
    count        = db.query(func.count(Review.id)).filter(Review.restaurant_id == restaurant_id).scalar()
    distribution = get_ratings_distribution(db, restaurant_id)
    sentiment    = simple_sentiment(all_reviews)

    return {
        "restaurant_id":        restaurant_id,
        "restaurant_name":      r.name,
        "total_views":          r.view_count or 0,
        "avg_rating":           round(float(avg), 1) if avg else 0,
        "total_reviews":        count or 0,
        "ratings_distribution": distribution,
        "sentiment":            sentiment,
    }


@router.post("/restaurants")
def post_restaurant(
    data: OwnerRestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(owner_only)
):
    r = Restaurant(**data.dict(), owner_id=current_user.id, is_claimed=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.put("/restaurants/{restaurant_id}")
def edit_restaurant(
    restaurant_id: int,
    data: OwnerRestaurantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(owner_only)
):
    r = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found or not yours")
    for k, v in data.dict(exclude_none=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.post("/restaurants/{restaurant_id}/photos")
def upload_owner_photo(
    restaurant_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(owner_only)
):
    r = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found or not yours")
    ext   = file.filename.split(".")[-1]
    fname = f"{uuid.uuid4()}.{ext}"
    path  = f"uploads/{fname}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    photo = RestaurantPhoto(restaurant_id=restaurant_id, photo_url=f"/{path}")
    db.add(photo)
    db.commit()
    return {"photo_url": photo.photo_url}


@router.get("/restaurants")
def get_my_restaurants(
    db: Session = Depends(get_db),
    current_user: User = Depends(owner_only)
):
    restaurants = db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).all()
    result = []
    for r in restaurants:
        avg    = db.query(func.avg(Review.rating)).filter(Review.restaurant_id == r.id).scalar()
        count  = db.query(func.count(Review.id)).filter(Review.restaurant_id == r.id).scalar()
        photos = [{"id": p.id, "photo_url": p.photo_url} for p in r.photos]
        result.append({
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
            "avg_rating":   round(float(avg), 1) if avg else 0,
            "review_count": count or 0,
            "photos":       photos,
        })
    return result


@router.get("/restaurants/{restaurant_id}/reviews")
def get_restaurant_reviews(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(owner_only)
):
    r = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found or not yours")

    reviews = db.query(Review).filter(
        Review.restaurant_id == restaurant_id
    ).order_by(Review.review_date.desc()).all()

    result = []
    for rev in reviews:
        reviewer = db.query(User).filter(User.id == rev.user_id).first()
        result.append({
            "id":            rev.id,
            "rating":        rev.rating,
            "comment":       rev.comment,
            "review_date":   rev.review_date,
            "updated_at":    rev.updated_at,
            "user_id":       rev.user_id,
            "reviewer_name": reviewer.name if reviewer else "Unknown",
            "reviewer_photo": reviewer.profile_picture if reviewer else None,
        })
    return result
