from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine
from app.models import *
import os

from app.routes import auth, users, restaurants, reviews, favorites, ai_assistant, owner

app = FastAPI(title="Yelp API")

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
app.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
app.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])
app.include_router(ai_assistant.router, prefix="/ai-assistant", tags=["AI Assistant"])
app.include_router(owner.router, prefix="/owner", tags=["Owner"])

@app.get("/")
def root():
    return {"message": "Yelp API is running"}
