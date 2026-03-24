# Yelp API

Backend for Yelp-style restaurant discovery platform built with FastAPI and MySQL.

## Tech Stack
- Python 3.11
- FastAPI
- MySQL
- SQLAlchemy
- JWT Authentication
- Langchain + Groq (AI Assistant)
- Tavily (Web Search)

## Setup

1. Clone the repo

2. Create a virtual environment:
   python -m venv venv
   venv\Scripts\activate  (Windows)
   source venv/bin/activate  (Mac/Linux)

3. Install dependencies:
   pip install -r requirements.txt

4. Create MySQL database and run schema:
   mysql -u root -p -e "CREATE DATABASE yelp_api;"
   mysql -u root -p yelp_api < schema.sql

5. Set up environment variables:
   cp .env.example .env
   Fill in your values in .env

6. Seed the database with sample data:
   python seed.py

7. Run the server:
   uvicorn main:app --reload

## API Documentation

Swagger UI is available at:
   http://localhost:8000/docs

All API endpoints can be viewed and tested directly from the Swagger UI.
Use the Authorize button in Swagger to login and test protected routes.

## API Endpoints

- POST /auth/signup
- POST /auth/login
- GET/PUT /users/me
- GET/PUT /users/me/preferences
- GET /users/me/history
- GET/POST /restaurants/
- GET/PUT /restaurants/{id}
- POST /restaurants/{id}/claim
- POST/GET/PUT/DELETE /reviews/
- GET/POST/DELETE /favorites/
- POST /ai-assistant/chat
- GET/DELETE /ai-assistant/history
- GET /owner/dashboard
- POST/PUT /owner/restaurants
