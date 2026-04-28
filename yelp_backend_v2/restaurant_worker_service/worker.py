import asyncio
import json
import os
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from bson import ObjectId

from app.mongodb import get_sync_db


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
GROUP_ID = os.getenv("KAFKA_RESTAURANT_GROUP_ID", "restaurant-worker-group")

TOPICS = ["restaurant.created"]


def parse_iso_datetime(value):
    if not value:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.utcnow()


def handle_restaurant_created(payload, db):
    restaurant_id = payload.get("restaurant_id")
    owner_id = payload.get("owner_id")
    name = payload.get("name")
    if not (restaurant_id and owner_id and name):
        return

    doc = {
        "_id": ObjectId(restaurant_id),
        "owner_id": ObjectId(owner_id),
        "name": name,
        "cuisine_type": payload.get("cuisine_type"),
        "address": payload.get("address"),
        "city": payload.get("city"),
        "state": payload.get("state"),
        "zip": payload.get("zip"),
        "description": payload.get("description"),
        "hours": payload.get("hours"),
        "contact": payload.get("contact"),
        "pricing_tier": payload.get("pricing_tier"),
        "amenities": payload.get("amenities"),
        "is_claimed": payload.get("is_claimed", False),
        "view_count": payload.get("view_count", 0),
        "created_at": parse_iso_datetime(payload.get("created_at")),
        "photos": payload.get("photos", [])
    }
    db.restaurants.update_one({"_id": doc["_id"]}, {"$setOnInsert": doc}, upsert=True)


async def consume():
    db = get_sync_db()
    consumer = AIOKafkaConsumer(
        *TOPICS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )
    await consumer.start()
    try:
        async for message in consumer:
            topic = message.topic
            payload = message.value
            if topic == "restaurant.created":
                handle_restaurant_created(payload, db)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume())
