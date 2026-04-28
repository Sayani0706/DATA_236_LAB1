import asyncio
import json
import os
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from bson import ObjectId

from app.mongodb import get_sync_db


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
GROUP_ID = os.getenv("KAFKA_USER_GROUP_ID", "user-worker-group")

TOPICS = ["user.created", "user.updated"]


def parse_iso_datetime(value):
    if not value:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.utcnow()


def handle_user_created(payload, db):
    user_id = payload.get("user_id")
    email = payload.get("email")
    if not (user_id and email):
        return

    doc = {
        "_id": ObjectId(user_id),
        "name": payload.get("name"),
        "email": email,
        "role": payload.get("role", "user"),
        "city": payload.get("city"),
        "created_at": parse_iso_datetime(payload.get("created_at")),
    }
    db.users.update_one({"_id": doc["_id"]}, {"$setOnInsert": doc}, upsert=True)


def handle_user_updated(payload, db):
    user_id = payload.get("user_id")
    updated_fields = payload.get("updated_fields") or {}
    if not user_id:
        return

    if updated_fields:
        updated_fields["updated_at"] = parse_iso_datetime(payload.get("updated_at"))
        db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updated_fields})


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
            if topic == "user.created":
                handle_user_created(payload, db)
            elif topic == "user.updated":
                handle_user_updated(payload, db)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume())
