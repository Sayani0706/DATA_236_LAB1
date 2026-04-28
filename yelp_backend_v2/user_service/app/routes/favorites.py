from fastapi import APIRouter, Depends, HTTPException
from app.mongodb import get_db
from app.utils.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()


@router.post("/{restaurant_id}")
async def add_favorite(restaurant_id: str, db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

    restaurant = await db.restaurants.find_one({"_id": rest_obj_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    existing = await db.favorites.find_one({
        "user_id": current_user["_id"],
        "restaurant_id": rest_obj_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")

    await db.favorites.insert_one({
        "user_id": current_user["_id"],
        "restaurant_id": rest_obj_id,
        "saved_at": datetime.utcnow()
    })

    return {"message": "Added to favorites"}


@router.delete("/{restaurant_id}")
async def remove_favorite(restaurant_id: str, db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        rest_obj_id = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

    result = await db.favorites.delete_one({
        "user_id": current_user["_id"],
        "restaurant_id": rest_obj_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not in favorites")

    return {"message": "Removed from favorites"}


@router.get("/")
async def get_favorites(db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    favorites = await db.favorites.find({"user_id": current_user["_id"]}).to_list(length=None)
    result = []

    for fav in favorites:
        restaurant = await db.restaurants.find_one({"_id": fav["restaurant_id"]})
        if not restaurant:
            continue

        pipeline = [
            {"$match": {"restaurant_id": fav["restaurant_id"]}},
            {"$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"},
                "count": {"$sum": 1}
            }}
        ]
        stats = await db.reviews.aggregate(pipeline).to_list(length=1)
        avg_rating = round(stats[0]["avg_rating"], 1) if stats and stats[0]["avg_rating"] else 0
        review_count = stats[0]["count"] if stats else 0

        result.append({
            "id": str(restaurant["_id"]),
            "name": restaurant["name"],
            "cuisine_type": restaurant.get("cuisine_type"),
            "address": restaurant.get("address"),
            "city": restaurant.get("city"),
            "state": restaurant.get("state"),
            "pricing_tier": restaurant.get("pricing_tier"),
            "description": restaurant.get("description"),
            "avg_rating": avg_rating,
            "review_count": review_count
        })

    return result
