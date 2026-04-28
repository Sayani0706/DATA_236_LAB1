from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pymongo import ASCENDING

from app.routes import auth, users, favorites, ai_assistant
from app.mongodb import get_sync_db
from app.kafka_producer import start_kafka_producer, stop_kafka_producer

app = FastAPI(title="User Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])
app.include_router(ai_assistant.router, prefix="/ai-assistant", tags=["AI Assistant"])


@app.on_event("startup")
def ensure_session_indexes():
    db = get_sync_db()
    db.sessions.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    db.sessions.create_index([("user_id", ASCENDING)])


@app.on_event("startup")
async def startup_event():
    await start_kafka_producer()


@app.on_event("shutdown")
async def shutdown_event():
    await stop_kafka_producer()

@app.get("/")
def root():
    return {"message": "User Service is running"}
