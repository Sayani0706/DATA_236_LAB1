import asyncio
import json
import os
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from bson import ObjectId

from app.mongodb import get_sync_db


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
GROUP_ID = os.getenv("KAFKA_REVIEW_GROUP_ID", "review-worker-group")

TOPICS = ["review.created", "review.updated", "review.deleted"]


def parse_iso_datetime(value):
    if not value:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.utcnow()


def handle_review_created(payload, db):
    review_id = payload.get("review_id")
    user_id = payload.get("user_id")
    restaurant_id = payload.get("restaurant_id")
    if not (review_id and user_id and restaurant_id):
        return

    doc = {
        "_id": ObjectId(review_id),
        "user_id": ObjectId(user_id),
        "restaurant_id": ObjectId(restaurant_id),
        "rating": payload.get("rating"),
        "comment": payload.get("comment"),
        "review_date": parse_iso_datetime(payload.get("review_date")),
        "updated_at": parse_iso_datetime(payload.get("updated_at")),
        "photos": []
    }
    db.reviews.update_one({"_id": doc["_id"]}, {"$setOnInsert": doc}, upsert=True)


def handle_review_updated(payload, db):
    review_id = payload.get("review_id")
    user_id = payload.get("user_id")
    if not (review_id and user_id):
        return

    update_fields = {}
    if "rating" in payload:
        update_fields["rating"] = payload.get("rating")
    if "comment" in payload:
        update_fields["comment"] = payload.get("comment")
    update_fields["updated_at"] = parse_iso_datetime(payload.get("updated_at"))

    db.reviews.update_one(
        {"_id": ObjectId(review_id), "user_id": ObjectId(user_id)},
        {"$set": update_fields}
    )


def handle_review_deleted(payload, db):
    review_id = payload.get("review_id")
    user_id = payload.get("user_id")
    if not (review_id and user_id):
        return

    db.reviews.delete_one({"_id": ObjectId(review_id), "user_id": ObjectId(user_id)})


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
            if topic == "review.created":
                handle_review_created(payload, db)
            elif topic == "review.updated":
                handle_review_updated(payload, db)
            elif topic == "review.deleted":
                handle_review_deleted(payload, db)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume())
