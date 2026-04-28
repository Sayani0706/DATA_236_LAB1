from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.preferences import UserPreference
from app.models.restaurant import Restaurant
from app.models.review import Review
from app.models.chat import ChatHistory
from app.utils.auth import get_current_user
from app.config import GROQ_API_KEY, TAVILY_API_KEY
from pydantic import BaseModel
from typing import List, Optional
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os, json

router = APIRouter()

os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []

def get_user_prefs(db, user_id):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if not prefs:
        return "No preferences set"
    return (
        f"Cuisine: {prefs.cuisines}, Price: {prefs.price_range}, "
        f"Dietary: {prefs.dietary_needs}, Ambiance: {prefs.ambiance}, "
        f"Location: {prefs.location}, Sort by: {prefs.sort_preference}"
    )

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

def extract_filters_with_llm(message, llm):
    # use LLM to extract filters from natural language
    extraction_prompt = f"""Extract restaurant search filters from this query. Return ONLY a JSON object with these keys (use null if not mentioned):
- cuisine: string (e.g. "Italian", "Chinese", "Japanese")
- dietary: string (e.g. "vegan", "vegetarian", "halal", "gluten-free")
- ambiance: string (e.g. "romantic", "casual", "family-friendly", "fine dining")
- price: string (use "$", "$$", "$$$", "$$$$" only)
- city: string (e.g. "San Jose", "San Francisco", "Oakland")
- keyword: string (any other relevant keyword)

Query: "{message}"

Return only valid JSON, nothing else."""

    try:
        response = llm.invoke([HumanMessage(content=extraction_prompt)])
        text = response.content.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        filters = json.loads(text)
        return filters
    except:
        return {}

def query_restaurants(db, cuisine=None, price=None, city=None, keyword=None, dietary=None):
    q = db.query(Restaurant)
    if cuisine:
        q = q.filter(Restaurant.cuisine_type.ilike(f"%{cuisine}%"))
    if price:
        q = q.filter(Restaurant.pricing_tier == price)
    if city:
        q = q.filter(Restaurant.city.ilike(f"%{city}%"))
    if keyword:
        q = q.filter(Restaurant.description.ilike(f"%{keyword}%") | Restaurant.amenities.ilike(f"%{keyword}%"))
    if dietary:
        q = q.filter(Restaurant.amenities.ilike(f"%{dietary}%") | Restaurant.description.ilike(f"%{dietary}%"))
    restaurants = q.limit(10).all()
    result = []
    for r in restaurants:
        avg = db.query(func.avg(Review.rating)).filter(Review.restaurant_id == r.id).scalar()
        result.append({
            "id": r.id,
            "name": r.name,
            "cuisine": r.cuisine_type,
            "city": r.city,
            "pricing_tier": r.pricing_tier,
            "description": r.description,
            "avg_rating": round(float(avg), 1) if avg else 0
        })
    return result

@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prefs = get_user_prefs(db, current_user.id)

    llm = get_llm()

    # step 1: use LLM to extract filters from message
    filters = extract_filters_with_llm(request.message, llm)

    # step 2: only query restaurants if the message has actual restaurant intent.
    # If all filters are null, check if it's a short/greeting message — if so, skip restaurant lookup.
    has_filters = any(v for v in filters.values() if v is not None)
    GREETING_PHRASES = {"hi", "hello", "hey", "hiya", "howdy", "sup", "what's up", "whats up", "yo", "good morning", "good evening", "good afternoon"}
    is_greeting = request.message.strip().lower() in GREETING_PHRASES or (
        len(request.message.strip().split()) <= 3 and not has_filters
    )

    restaurants = []
    if has_filters or not is_greeting:
        restaurants = query_restaurants(
            db,
            cuisine=filters.get("cuisine"),
            price=filters.get("price"),
            city=filters.get("city"),
            keyword=filters.get("keyword") or filters.get("ambiance"),
            dietary=filters.get("dietary")
        )

    restaurant_context = ""
    if restaurants:
        restaurant_context = "\n".join([
            f"- {r['name']} ({r['cuisine']}, {r['pricing_tier']}, {r['avg_rating']}★, {r['city']}): {r['description']}"
            for r in restaurants
        ])

    # step 3: run Tavily search BEFORE LLM for extra context (only for non-greetings)
    web_context = ""
    if not is_greeting:
        try:
            tavily = TavilySearchResults(max_results=2)
            search_results = tavily.invoke(request.message)
            web_context = " ".join([r.get("content", "") for r in search_results])[:600]
        except:
            web_context = ""

    # step 4: build system prompt — only inject restaurant data if we have it
    if restaurant_context:
        system_content = f"""You are a helpful restaurant recommendation assistant for a Yelp-like platform.
User preferences: {prefs}
Available restaurants in database:
{restaurant_context}
{f'Additional web context: {web_context}' if web_context else ''}
Use the user preferences and web context to personalize recommendations.
Always respond in a conversational, helpful tone.
When recommending restaurants, include name, rating, price tier, and a brief reason why it matches."""
    else:
        system_content = """You are a helpful restaurant recommendation assistant for a Yelp-like platform.
Respond in a conversational, friendly tone. If the user greets you, greet them back and ask how you can help them find a restaurant.
If they ask a restaurant-related question, ask clarifying questions about cuisine, location, budget, or occasion."""

    messages = [SystemMessage(content=system_content)]

    for msg in request.conversation_history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))

    messages.append(HumanMessage(content=request.message))

    try:
        response = llm.invoke(messages)
        reply = response.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

    db.add(ChatHistory(user_id=current_user.id, message=request.message, role="user"))
    db.add(ChatHistory(user_id=current_user.id, message=reply, role="assistant"))
    db.commit()

    # always return all queried restaurants (not just name-matched ones)
    return {
        "response": reply,
        "recommendations": restaurants,
        "web_context": web_context if web_context else None
    }

@router.get("/history")
def get_chat_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at).all()

@router.delete("/history")
def clear_chat_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Chat history cleared"}
