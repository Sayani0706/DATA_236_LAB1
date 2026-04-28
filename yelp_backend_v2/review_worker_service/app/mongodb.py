import os

from pymongo import MongoClient


MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "yelp_db")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]


def get_sync_db():
    return db
