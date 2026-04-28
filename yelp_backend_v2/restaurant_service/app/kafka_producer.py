import json
import os
from typing import Any, Dict

from aiokafka import AIOKafkaProducer


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

producer: AIOKafkaProducer | None = None


async def start_kafka_producer() -> None:
    global producer
    if producer is not None:
        return

    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )
    await producer.start()


async def stop_kafka_producer() -> None:
    global producer
    if producer is None:
        return

    await producer.stop()
    producer = None


async def publish_event(topic: str, payload: Dict[str, Any]) -> None:
    if producer is None:
        raise RuntimeError("Kafka producer is not started")

    await producer.send_and_wait(topic, payload)
