from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routes import reviews
from app.kafka_producer import start_kafka_producer, stop_kafka_producer

app = FastAPI(title="Review Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])


@app.on_event("startup")
async def startup_event():
    await start_kafka_producer()


@app.on_event("shutdown")
async def shutdown_event():
    await stop_kafka_producer()

@app.get("/")
def root():
    return {"message": "Review Service is running"}
