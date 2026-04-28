from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "yelp_db")

async_client = AsyncIOMotorClient(MONGO_URL)
async_db = async_client[DB_NAME]

sync_client = MongoClient(MONGO_URL)
sync_db = sync_client[DB_NAME]


def get_db():
    return async_db


def get_sync_db():
    return sync_db
