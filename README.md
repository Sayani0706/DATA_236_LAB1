# Yelp Clone - Restaurant Discovery Platform

A Yelp-style restaurant discovery and review platform built with React, FastAPI, MySQL, and an AI Assistant powered by LangChain, Groq, and Tavily.

---

## Tech Stack

| Layer          | Technology                                      |
|----------------|-------------------------------------------------|
| Frontend       | React, Bootstrap 5, Axios, React Router v6      |
| Backend        | Python, FastAPI, SQLAlchemy                     |
| Database       | MySQL                                           |
| Authentication | JWT (JSON Web Tokens), bcrypt                   |
| AI Assistant   | LangChain, Groq (llama-3.3-70b), Tavily Search  |

---

## Project Structure

```
DATA236_LAB1/
├── yelp_frontend/       # React frontend
├── yelp_backend/        # FastAPI backend
└── README.md
```

---

## Prerequisites

- Python 3.10+
- Node.js 16+
- MySQL 8+
- A Groq API key — https://console.groq.com
- A Tavily API key — https://app.tavily.com

---

## Backend Setup

### 1. Navigate to backend folder
```bash
cd yelp_backend
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Copy `.env.example` to `.env` and fill in your database credentials and API keys.

### 4. Set up the database
```bash
mysql -u root -p < schema.sql
```

### 5. (Optional) Seed sample data
```bash
python seed.py
```

### 6. Start the backend server
```bash
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000

Swagger API docs at: http://localhost:8000/docs

---

## Frontend Setup

### 1. Navigate to frontend folder
```bash
cd yelp_frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure environment variables
Create a `.env` file in the `yelp_frontend` folder:
```
REACT_APP_API_URL=http://localhost:8000
```

### 4. Start the frontend
```bash
npm start
```

Frontend runs at: http://localhost:3000

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/signup | Register as user or owner |
| POST | /auth/login | Login and receive JWT token |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /users/me | Get current user profile |
| PUT | /users/me | Update profile |
| POST | /users/me/photo | Upload profile picture |
| GET | /users/me/preferences | Get AI preferences |
| PUT | /users/me/preferences | Save AI preferences |
| GET | /users/me/history | Get user history |

### Restaurants
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /restaurants/ | Search and filter restaurants |
| GET | /restaurants/{id} | Get restaurant details |
| POST | /restaurants/ | Create a restaurant listing |
| PUT | /restaurants/{id} | Update a restaurant |
| POST | /restaurants/{id}/photos | Upload restaurant photo |
| POST | /restaurants/{id}/claim | Claim a restaurant |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /reviews/ | Create a review |
| GET | /reviews/restaurant/{id} | List reviews for a restaurant |
| PUT | /reviews/{id} | Update own review |
| DELETE | /reviews/{id} | Delete own review |
| POST | /reviews/{id}/photos | Attach photo to review |

### Favorites
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /favorites/ | List favorites |
| POST | /favorites/{id} | Add to favorites |
| DELETE | /favorites/{id} | Remove from favorites |

### Owner
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /owner/dashboard | Owner analytics dashboard |
| GET | /owner/restaurants | List owned restaurants |
| POST | /owner/restaurants | Add restaurant (auto-claimed) |
| PUT | /owner/restaurants/{id} | Edit restaurant |
| POST | /owner/restaurants/{id}/photos | Upload photo |
| GET | /owner/restaurants/{id}/reviews | View reviews (read-only) |

### AI Assistant
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /ai-assistant/chat | Send message to AI chatbot |
| GET | /ai-assistant/history | Get chat history |
| DELETE | /ai-assistant/history | Clear chat history |

---

## Features

### User Features
- Signup and login with JWT authentication
- Profile management with photo upload
- AI Assistant preferences (cuisine, price, dietary, ambiance, location, sort)
- Restaurant search by name, cuisine, keyword, city, ZIP
- Restaurant details with photos, hours, contact, reviews
- Add restaurant listings with photos
- Write, edit, and delete reviews with optional photos
- Save and manage favourite restaurants
- View history of reviews and restaurants added

### Restaurant Owner Features
- Owner signup and login
- Add and edit restaurant listings (auto-claimed)
- Claim existing unclaimed restaurants
- Owner dashboard with analytics:
  - Average rating
  - Total reviews
  - Total views
  - Ratings distribution (1-5 stars)
  - Sentiment analysis (Positive / Neutral / Negative)
- View all reviews for owned restaurants (read-only)

### AI Assistant
- Conversational chatbot on home and explore pages
- Loads user preferences from database automatically
- Natural language query interpretation using LangChain + Groq
- Extracts filters: cuisine, price, dietary, ambiance, city
- Queries restaurant database and ranks results
- Tavily web search for additional real-world context
- Supports multi-turn conversations
- Quick action buttons: Find dinner tonight, Best rated near me, Vegan options
- Clickable restaurant cards linking to details page

---

## Database Schema

- users
- user_preferences
- restaurants
- restaurant_photos
- reviews
- review_photos
- favorites
- chat_history
