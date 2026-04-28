from fastapi import APIRouter, Depends, HTTPException
from app.mongodb import get_db
from app.utils.auth import get_current_user
from app.config import GROQ_API_KEY, TAVILY_API_KEY
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os, json

router = APIRouter()

os.environ["GROQ_API_KEY"] = GROQ_API_KEY or ""
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY or ""


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


async def get_user_prefs(db, user_id):
    user = await db.users.find_one({"_id": user_id})
    if not user or not user.get("preferences"):
        return "No preferences set"
    prefs = user["preferences"]
    return (
        f"Cuisine: {prefs.get('cuisines')}, Price: {prefs.get('price_range')}, "
        f"Dietary: {prefs.get('dietary_needs')}, Ambiance: {prefs.get('ambiance')}, "
        f"Location: {prefs.get('location')}, Sort by: {prefs.get('sort_preference')}"
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
        return json.loads(text)
    except Exception:
        return {}


async def query_restaurants(db, cuisine=None, price=None, city=None, keyword=None, dietary=None):
    query_filter = {}
    if cuisine:
        query_filter["cuisine_type"] = {"$regex": cuisine, "$options": "i"}
    if price:
        query_filter["pricing_tier"] = price
    if city:
        query_filter["city"] = {"$regex": city, "$options": "i"}
    if keyword:
        query_filter["$or"] = [
            {"description": {"$regex": keyword, "$options": "i"}},
            {"amenities": {"$regex": keyword, "$options": "i"}}
        ]
    if dietary:
        if "$or" in query_filter:
            query_filter["$and"] = [
                {"$or": query_filter.pop("$or")},
                {"$or": [
                    {"amenities": {"$regex": dietary, "$options": "i"}},
                    {"description": {"$regex": dietary, "$options": "i"}}
                ]}
            ]
        else:
            query_filter["$or"] = [
                {"amenities": {"$regex": dietary, "$options": "i"}},
                {"description": {"$regex": dietary, "$options": "i"}}
            ]

    restaurants = await db.restaurants.find(query_filter).limit(10).to_list(length=None)
    result = []
    for r in restaurants:
        pipeline = [
            {"$match": {"restaurant_id": r["_id"]}},
            {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
        ]
        stats = await db.reviews.aggregate(pipeline).to_list(length=1)
        avg = round(stats[0]["avg_rating"], 1) if stats and stats[0]["avg_rating"] else 0
        result.append({
            "id": str(r["_id"]),
            "name": r["name"],
            "cuisine": r.get("cuisine_type"),
            "city": r.get("city"),
            "pricing_tier": r.get("pricing_tier"),
            "description": r.get("description"),
            "avg_rating": avg
        })
    return result


@router.post("/chat")
async def chat(request: ChatRequest, db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    prefs = await get_user_prefs(db, current_user["_id"])
    llm = get_llm()
    filters = extract_filters_with_llm(request.message, llm)

    has_filters = any(v for v in filters.values() if v is not None)
    greetings = {"hi", "hello", "hey", "hiya", "howdy", "sup", "what's up", "whats up", "yo", "good morning", "good evening", "good afternoon"}
    is_greeting = request.message.strip().lower() in greetings or (
        len(request.message.strip().split()) <= 3 and not has_filters
    )

    restaurants = []
    if has_filters or not is_greeting:
        restaurants = await query_restaurants(
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

    web_context = ""
    if not is_greeting:
        try:
            tavily = TavilySearchResults(max_results=2)
            search_results = tavily.invoke(request.message)
            web_context = " ".join([r.get("content", "") for r in search_results])[:600]
        except Exception:
            web_context = ""

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

    await db.chat_history.insert_one({
        "user_id": current_user["_id"],
        "message": request.message,
        "role": "user",
        "created_at": datetime.utcnow()
    })
    await db.chat_history.insert_one({
        "user_id": current_user["_id"],
        "message": reply,
        "role": "assistant",
        "created_at": datetime.utcnow()
    })

    return {
        "response": reply,
        "recommendations": restaurants,
        "web_context": web_context if web_context else None
    }


@router.get("/history")
async def get_chat_history(db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    history = await db.chat_history.find({"user_id": current_user["_id"]}).sort("created_at", 1).to_list(length=None)
    return [
        {
            "id": str(h["_id"]),
            "user_id": str(h["user_id"]),
            "message": h["message"],
            "role": h["role"],
            "created_at": h.get("created_at")
        }
        for h in history
    ]


@router.delete("/history")
async def clear_chat_history(db = Depends(get_db), current_user: dict = Depends(get_current_user)):
    await db.chat_history.delete_many({"user_id": current_user["_id"]})
    return {"message": "Chat history cleared"}
