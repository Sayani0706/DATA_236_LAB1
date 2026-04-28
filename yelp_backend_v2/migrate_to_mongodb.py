import mysql.connector
from pymongo import MongoClient, ASCENDING, TEXT
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

mysql_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "yelp_api")
}

mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
mongo_db_name = os.getenv("MONGO_DB_NAME", "yelp_db")

mysql_conn = mysql.connector.connect(**mysql_config)
mysql_cursor = mysql_conn.cursor(dictionary=True)

mongo_client = MongoClient(mongo_url)
mongo_db = mongo_client[mongo_db_name]

user_id_map = {}
restaurant_id_map = {}
review_id_map = {}

def migrate_users():
    print("Migrating users...")
    mysql_cursor.execute("SELECT * FROM users")
    users = mysql_cursor.fetchall()
    
    for user in users:
        mysql_cursor.execute(
            "SELECT * FROM user_preferences WHERE user_id = %s",
            (user['id'],)
        )
        prefs = mysql_cursor.fetchone()
        
        user_doc = {
            "name": user['name'],
            "email": user['email'],
            "password": user['password'],
            "role": user['role'],
            "phone": user.get('phone'),
            "about_me": user.get('about_me'),
            "city": user.get('city'),
            "state": user.get('state'),
            "country": user.get('country'),
            "languages": user.get('languages'),
            "gender": user.get('gender'),
            "profile_picture": user.get('profile_picture'),
            "created_at": user['created_at'] if user['created_at'] else datetime.utcnow(),
            "preferences": {}
        }
        
        if prefs:
            user_doc["preferences"] = {
                "cuisines": prefs.get('cuisines'),
                "price_range": prefs.get('price_range'),
                "location": prefs.get('location'),
                "search_radius": prefs.get('search_radius'),
                "dietary_needs": prefs.get('dietary_needs'),
                "ambiance": prefs.get('ambiance'),
                "sort_preference": prefs.get('sort_preference')
            }
        
        result = mongo_db.users.insert_one(user_doc)
        user_id_map[user['id']] = result.inserted_id
    
    mongo_db.users.create_index([("email", ASCENDING)], unique=True)
    mongo_db.users.create_index([("role", ASCENDING)])
    
    print(f"Migrated {len(users)} users")

def migrate_restaurants():
    print("Migrating restaurants...")
    mysql_cursor.execute("SELECT * FROM restaurants")
    restaurants = mysql_cursor.fetchall()
    
    for rest in restaurants:
        mysql_cursor.execute(
            "SELECT photo_url, uploaded_at FROM restaurant_photos WHERE restaurant_id = %s",
            (rest['id'],)
        )
        photos = mysql_cursor.fetchall()
        
        rest_doc = {
            "owner_id": user_id_map.get(rest['owner_id']) if rest['owner_id'] else None,
            "name": rest['name'],
            "cuisine_type": rest.get('cuisine_type'),
            "address": rest.get('address'),
            "city": rest.get('city'),
            "state": rest.get('state'),
            "zip": rest.get('zip'),
            "description": rest.get('description'),
            "hours": rest.get('hours'),
            "contact": rest.get('contact'),
            "pricing_tier": rest.get('pricing_tier'),
            "amenities": rest.get('amenities'),
            "is_claimed": bool(rest.get('is_claimed', False)),
            "view_count": rest.get('view_count', 0),
            "created_at": rest['created_at'] if rest['created_at'] else datetime.utcnow(),
            "photos": [
                {
                    "photo_url": p['photo_url'],
                    "uploaded_at": p['uploaded_at'] if p['uploaded_at'] else datetime.utcnow()
                }
                for p in photos
            ]
        }
        
        result = mongo_db.restaurants.insert_one(rest_doc)
        restaurant_id_map[rest['id']] = result.inserted_id
    
    mongo_db.restaurants.create_index([("owner_id", ASCENDING)])
    mongo_db.restaurants.create_index([("name", TEXT)])
    mongo_db.restaurants.create_index([("cuisine_type", ASCENDING)])
    mongo_db.restaurants.create_index([("city", ASCENDING)])
    
    print(f"Migrated {len(restaurants)} restaurants")

def migrate_reviews():
    print("Migrating reviews...")
    mysql_cursor.execute("SELECT * FROM reviews")
    reviews = mysql_cursor.fetchall()
    
    for rev in reviews:
        mysql_cursor.execute(
            "SELECT photo_url FROM review_photos WHERE review_id = %s",
            (rev['id'],)
        )
        photos = mysql_cursor.fetchall()
        
        review_doc = {
            "user_id": user_id_map.get(rev['user_id']),
            "restaurant_id": restaurant_id_map.get(rev['restaurant_id']),
            "rating": rev['rating'],
            "comment": rev.get('comment'),
            "review_date": rev['review_date'] if rev['review_date'] else datetime.utcnow(),
            "updated_at": rev['updated_at'] if rev['updated_at'] else datetime.utcnow(),
            "photos": [{"photo_url": p['photo_url']} for p in photos]
        }
        
        result = mongo_db.reviews.insert_one(review_doc)
        review_id_map[rev['id']] = result.inserted_id
    
    mongo_db.reviews.create_index([("user_id", ASCENDING)])
    mongo_db.reviews.create_index([("restaurant_id", ASCENDING)])
    mongo_db.reviews.create_index(
        [("user_id", ASCENDING), ("restaurant_id", ASCENDING)],
        unique=True
    )
    
    print(f"Migrated {len(reviews)} reviews")

def migrate_favorites():
    print("Migrating favorites...")
    mysql_cursor.execute("SELECT * FROM favorites")
    favorites = mysql_cursor.fetchall()
    
    for fav in favorites:
        fav_doc = {
            "user_id": user_id_map.get(fav['user_id']),
            "restaurant_id": restaurant_id_map.get(fav['restaurant_id']),
            "saved_at": fav['saved_at'] if fav['saved_at'] else datetime.utcnow()
        }
        mongo_db.favorites.insert_one(fav_doc)
    
    mongo_db.favorites.create_index([("user_id", ASCENDING)])
    mongo_db.favorites.create_index(
        [("user_id", ASCENDING), ("restaurant_id", ASCENDING)],
        unique=True
    )
    
    print(f"Migrated {len(favorites)} favorites")

def migrate_chat_history():
    print("Migrating chat history...")
    mysql_cursor.execute("SELECT * FROM chat_history")
    chats = mysql_cursor.fetchall()
    
    for chat in chats:
        chat_doc = {
            "user_id": user_id_map.get(chat['user_id']),
            "message": chat['message'],
            "role": chat['role'],
            "created_at": chat['created_at'] if chat['created_at'] else datetime.utcnow()
        }
        mongo_db.chat_history.insert_one(chat_doc)
    
    mongo_db.chat_history.create_index([("user_id", ASCENDING)])
    mongo_db.chat_history.create_index([("created_at", ASCENDING)])
    
    print(f"Migrated {len(chats)} chat messages")

def create_sessions_collection():
    print("Creating sessions collection...")
    mongo_db.sessions.create_index([("user_id", ASCENDING)])
    mongo_db.sessions.create_index([("token", ASCENDING)], unique=True)
    mongo_db.sessions.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    print("Sessions collection created with TTL index")

def main():
    print("Starting MongoDB migration...")
    print(f"MySQL: {mysql_config['database']}")
    print(f"MongoDB: {mongo_db_name}")
    print()
    
    migrate_users()
    migrate_restaurants()
    migrate_reviews()
    migrate_favorites()
    migrate_chat_history()
    create_sessions_collection()
    
    print()
    print("Migration completed successfully!")
    print(f"Users: {mongo_db.users.count_documents({})}")
    print(f"Restaurants: {mongo_db.restaurants.count_documents({})}")
    print(f"Reviews: {mongo_db.reviews.count_documents({})}")
    print(f"Favorites: {mongo_db.favorites.count_documents({})}")
    print(f"Chat History: {mongo_db.chat_history.count_documents({})}")
    
    mysql_cursor.close()
    mysql_conn.close()
    mongo_client.close()

if __name__ == "__main__":
    main()
