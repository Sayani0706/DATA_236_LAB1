import os
import random
from datetime import datetime, timezone
from pymongo import MongoClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


def get_db():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:37017")
    db_name = os.getenv("MONGO_DB_NAME", "yelp_db")
    client = MongoClient(mongo_url)
    return client, client[db_name]


def seed_users(db):
    users_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "password": "pass123", "role": "user", "city": "San Jose", "state": "CA", "country": "United States", "gender": "Female", "languages": "English"},
        {"name": "Bob Smith", "email": "bob@example.com", "password": "pass123", "role": "user", "city": "San Francisco", "state": "CA", "country": "United States", "gender": "Male", "languages": "English, Spanish"},
        {"name": "Emily Chen", "email": "emily@example.com", "password": "pass123", "role": "user", "city": "San Jose", "state": "CA", "country": "United States", "gender": "Female", "languages": "English, Chinese"},
        {"name": "James Wilson", "email": "james@example.com", "password": "pass123", "role": "user", "city": "Oakland", "state": "CA", "country": "United States", "gender": "Male", "languages": "English"},
        {"name": "Sofia Martinez", "email": "sofia@example.com", "password": "pass123", "role": "user", "city": "San Jose", "state": "CA", "country": "United States", "gender": "Female", "languages": "English, Spanish"},
        {"name": "Carol White", "email": "carol@example.com", "password": "pass123", "role": "owner", "city": "San Jose", "state": "CA", "country": "United States", "gender": "Female", "languages": "English"},
        {"name": "David Lee", "email": "david@example.com", "password": "pass123", "role": "owner", "city": "San Francisco", "state": "CA", "country": "United States", "gender": "Male", "languages": "English, Chinese"},
        {"name": "Raj Patel", "email": "raj@example.com", "password": "pass123", "role": "owner", "city": "San Jose", "state": "CA", "country": "United States", "gender": "Male", "languages": "English, Hindi"},
        {"name": "Maria Garcia", "email": "maria@example.com", "password": "pass123", "role": "owner", "city": "Oakland", "state": "CA", "country": "United States", "gender": "Female", "languages": "English, Spanish"},
    ]
    prefs_by_email = {
        "alice@example.com": {"cuisines": "Italian, Mexican", "price_range": "$$", "location": "San Jose, CA", "search_radius": 10, "dietary_needs": "none", "ambiance": "casual", "sort_preference": "rating"},
        "bob@example.com": {"cuisines": "Chinese, Japanese", "price_range": "$$$", "location": "San Francisco, CA", "search_radius": 15, "dietary_needs": "vegetarian", "ambiance": "fine dining", "sort_preference": "popularity"},
        "emily@example.com": {"cuisines": "Korean, Japanese", "price_range": "$$", "location": "San Jose, CA", "search_radius": 10, "dietary_needs": "none", "ambiance": "casual", "sort_preference": "rating"},
        "james@example.com": {"cuisines": "American, Italian", "price_range": "$", "location": "Oakland, CA", "search_radius": 5, "dietary_needs": "none", "ambiance": "casual", "sort_preference": "price"},
        "sofia@example.com": {"cuisines": "Mexican, Mediterranean", "price_range": "$$", "location": "San Jose, CA", "search_radius": 10, "dietary_needs": "vegetarian", "ambiance": "family-friendly", "sort_preference": "rating"},
    }

    users = []
    for u in users_data:
        existing = db.users.find_one({"email": u["email"]})
        if existing:
            users.append(existing)
            continue

        doc = {
            "name": u["name"],
            "email": u["email"],
            "password": hash_password(u["password"]),
            "role": u["role"],
            "city": u["city"],
            "state": u["state"],
            "country": u["country"],
            "gender": u["gender"],
            "languages": u["languages"],
            "phone": None,
            "about_me": None,
            "profile_picture": None,
            "created_at": datetime.now(timezone.utc),
            "preferences": prefs_by_email.get(u["email"], {}),
        }
        result = db.users.insert_one(doc)
        doc["_id"] = result.inserted_id
        users.append(doc)
    return users


def seed_restaurants(db, owner_ids):
    restaurants_data = [
        {"name": "Pasta Paradise", "cuisine_type": "Italian", "address": "123 Main St", "city": "San Jose", "state": "CA", "zip": "95101", "description": "Authentic Italian pasta and wood-fired pizzas in a cozy setting", "hours": "Mon-Sun 11am-10pm", "contact": "408-111-2222", "pricing_tier": "$$", "amenities": "wifi, outdoor seating, romantic"},
        {"name": "Trattoria Roma", "cuisine_type": "Italian", "address": "456 Oak Ave", "city": "San Jose", "state": "CA", "zip": "95112", "description": "Family-owned Italian trattoria serving classic Roman dishes since 1995", "hours": "Tue-Sun 12pm-9pm", "contact": "408-222-3333", "pricing_tier": "$$", "amenities": "family-friendly, parking, wine bar"},
        {"name": "La Bella Italia", "cuisine_type": "Italian", "address": "789 Vineyard Rd", "city": "San Francisco", "state": "CA", "zip": "94102", "description": "Northern Italian cuisine with handmade pasta and seasonal ingredients", "hours": "Mon-Sat 5pm-11pm", "contact": "415-111-2222", "pricing_tier": "$$$", "amenities": "romantic, fine dining, wine cellar"},
        {"name": "Pizzeria Napoli", "cuisine_type": "Italian", "address": "321 Napoli Ln", "city": "San Jose", "state": "CA", "zip": "95128", "description": "Authentic Neapolitan pizza baked in a traditional wood-fired oven", "hours": "Mon-Sun 11am-11pm", "contact": "408-333-4444", "pricing_tier": "$", "amenities": "casual, takeout, delivery, family-friendly"},
        {"name": "Osteria Firenze", "cuisine_type": "Italian", "address": "654 Florence St", "city": "Oakland", "state": "CA", "zip": "94601", "description": "Tuscan-inspired dishes with fresh truffles and premium Italian wines", "hours": "Tue-Sun 5pm-10pm", "contact": "510-111-2222", "pricing_tier": "$$$", "amenities": "fine dining, romantic, reservations required"},
        {"name": "Mama Mia Kitchen", "cuisine_type": "Italian", "address": "987 Oregano Blvd", "city": "San Jose", "state": "CA", "zip": "95110", "description": "Home-style Italian cooking with generous portions and warm hospitality", "hours": "Mon-Sun 10am-10pm", "contact": "408-444-5555", "pricing_tier": "$", "amenities": "casual, family-friendly, takeout, delivery"},
        {"name": "Dragon Palace", "cuisine_type": "Chinese", "address": "789 Elm St", "city": "San Francisco", "state": "CA", "zip": "94102", "description": "Traditional Chinese cuisine with dim sum and Cantonese specialties", "hours": "Mon-Sun 10am-11pm", "contact": "415-333-4444", "pricing_tier": "$", "amenities": "family-friendly, takeout, delivery"},
        {"name": "Golden Phoenix", "cuisine_type": "Chinese", "address": "258 Lotus Ave", "city": "San Jose", "state": "CA", "zip": "95116", "description": "Authentic Cantonese seafood and dim sum in a spacious dining hall", "hours": "Mon-Sun 9am-10pm", "contact": "408-555-6666", "pricing_tier": "$$", "amenities": "family-friendly, parking, dim sum"},
        {"name": "Sakura Garden", "cuisine_type": "Japanese", "address": "321 Pine St", "city": "San Francisco", "state": "CA", "zip": "94103", "description": "Premium sushi and Japanese kaiseki cuisine in an elegant atmosphere", "hours": "Mon-Sat 5pm-11pm", "contact": "415-444-5555", "pricing_tier": "$$$", "amenities": "fine dining, sake bar, romantic"},
        {"name": "Ramen Republic", "cuisine_type": "Japanese", "address": "963 Broth Blvd", "city": "San Jose", "state": "CA", "zip": "95129", "description": "Rich tonkotsu and miso ramen with slow-cooked broths and fresh toppings", "hours": "Mon-Sun 11am-11pm", "contact": "408-888-9999", "pricing_tier": "$", "amenities": "casual, takeout, late night"},
        {"name": "Taco Fiesta", "cuisine_type": "Mexican", "address": "654 Maple Ave", "city": "San Jose", "state": "CA", "zip": "95110", "description": "Authentic street tacos and traditional Mexican dishes with vibrant atmosphere", "hours": "Mon-Sun 9am-10pm", "contact": "408-555-6666", "pricing_tier": "$", "amenities": "casual, outdoor seating, family-friendly"},
        {"name": "Casa Mexicana", "cuisine_type": "Mexican", "address": "741 Fiesta Rd", "city": "San Francisco", "state": "CA", "zip": "94105", "description": "Upscale Mexican cuisine with modern interpretations of classic dishes", "hours": "Mon-Sun 11am-10pm", "contact": "415-666-7777", "pricing_tier": "$$", "amenities": "casual, margarita bar, outdoor seating"},
        {"name": "Spice Route", "cuisine_type": "Indian", "address": "258 Saffron St", "city": "San Jose", "state": "CA", "zip": "95116", "description": "Rich and aromatic Indian curries and tandoor specialties from North and South India", "hours": "Mon-Sun 11:30am-10pm", "contact": "408-888-9999", "pricing_tier": "$$", "amenities": "halal, vegetarian options, family-friendly"},
        {"name": "Green Leaf Cafe", "cuisine_type": "American", "address": "987 Cedar Rd", "city": "San Jose", "state": "CA", "zip": "95128", "description": "100% vegan menu with fresh organic ingredients and casual atmosphere", "hours": "Mon-Fri 8am-8pm, Sat-Sun 9am-7pm", "contact": "408-666-7777", "pricing_tier": "$", "amenities": "vegan, vegetarian, gluten-free, casual, wifi"},
        {"name": "Candlelight Bistro", "cuisine_type": "French", "address": "147 Rosewood Ln", "city": "San Francisco", "state": "CA", "zip": "94104", "description": "Romantic French bistro with candlelit tables and classic French cuisine", "hours": "Tue-Sun 5pm-11pm", "contact": "415-777-8888", "pricing_tier": "$$$", "amenities": "romantic, fine dining, wine cellar"},
    ]

    restaurants = []
    for i, r in enumerate(restaurants_data):
        existing = db.restaurants.find_one({"name": r["name"]})
        if existing:
            restaurants.append(existing)
            continue

        doc = {
            **r,
            "owner_id": owner_ids[i % len(owner_ids)],
            "is_claimed": True,
            "view_count": 0,
            "photos": [],
            "created_at": datetime.now(timezone.utc),
        }
        result = db.restaurants.insert_one(doc)
        doc["_id"] = result.inserted_id
        restaurants.append(doc)
    return restaurants


def seed_reviews(db, reviewer_ids, restaurants):
    review_comments = [
        "Absolutely loved it! Will definitely come back.",
        "Great food and service. Highly recommend!",
        "Authentic flavors and generous portions.",
        "Fantastic experience overall.",
        "Solid place, worth visiting.",
    ]

    for i, restaurant in enumerate(restaurants):
        num_reviews = random.randint(2, 4)
        used = set()

        for j in range(num_reviews):
            reviewer_id = reviewer_ids[j % len(reviewer_ids)]
            if reviewer_id in used:
                continue
            used.add(reviewer_id)

            existing = db.reviews.find_one({
                "user_id": reviewer_id,
                "restaurant_id": restaurant["_id"],
            })
            if existing:
                continue

            now = datetime.now(timezone.utc).isoformat()
            db.reviews.insert_one({
                "user_id": reviewer_id,
                "restaurant_id": restaurant["_id"],
                "rating": random.randint(3, 5),
                "comment": review_comments[(i + j) % len(review_comments)],
                "review_date": now,
                "updated_at": now,
                "photos": [],
            })


def main():
    client, db = get_db()
    try:
        users = seed_users(db)
        owner_ids = [u["_id"] for u in users if u.get("role") == "owner"]
        reviewer_ids = [u["_id"] for u in users if u.get("role") == "user"]

        restaurants = seed_restaurants(db, owner_ids)
        seed_reviews(db, reviewer_ids, restaurants)

        print("Seed completed successfully")
        print(f"Users: {db.users.count_documents({})}")
        print(f"Restaurants: {db.restaurants.count_documents({})}")
        print(f"Reviews: {db.reviews.count_documents({})}")
    finally:
        client.close()


if __name__ == "__main__":
    main()