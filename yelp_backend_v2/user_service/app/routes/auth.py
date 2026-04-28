from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.mongodb import get_db
from app.utils.auth import (
    hash_password,
    verify_password,
    create_session_token,
    oauth2_scheme,
)
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from jose import JWTError, jwt
from bson import ObjectId
from app.config import SECRET_KEY, ALGORITHM
from app.kafka_producer import publish_event

router = APIRouter()

VALID_ROLES = {"user", "owner"}


class SignupData(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "user"
    restaurant_location: Optional[str] = None


class LoginData(BaseModel):
    email: EmailStr
    password: str


async def create_session(db, user_id: str, session_id: str, expires_at: datetime):
    await db.sessions.update_one(
        {"_id": session_id},
        {
            "$set": {
                "user_id": ObjectId(user_id),
                "created_at": datetime.utcnow(),
                "expires_at": expires_at,
                "is_revoked": False,
            }
        },
        upsert=True,
    )


@router.post("/signup")
async def signup(data: SignupData, db=Depends(get_db)):
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'owner'")

    existing_user = await db.users.find_one({"email": data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password),
        "role": data.role,
        "phone": None,
        "about_me": None,
        "city": data.restaurant_location if data.role == "owner" else None,
        "state": None,
        "country": None,
        "languages": None,
        "gender": None,
        "profile_picture": None,
        "created_at": datetime.utcnow(),
        "preferences": {},
    }

    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    event = {
        "user_id": user_id,
        "name": data.name,
        "email": data.email,
        "role": data.role,
        "city": user_doc.get("city"),
        "created_at": user_doc["created_at"].isoformat(),
    }
    try:
        await publish_event("user.created", event)
    except Exception:
        raise HTTPException(status_code=503, detail="Failed to queue user event")

    token, session_id, expires_at = create_session_token(user_id)
    await create_session(db, user_id, session_id, expires_at)
    return {"access_token": token, "token_type": "bearer", "role": data.role}


@router.post("/login")
async def login(data: LoginData, db=Depends(get_db)):
    user = await db.users.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    token, session_id, expires_at = create_session_token(user_id)
    await create_session(db, user_id, session_id, expires_at)
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}


@router.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = str(user["_id"])
    token, session_id, expires_at = create_session_token(user_id)
    await create_session(db, user_id, session_id, expires_at)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        session_id = payload.get("sid")
        user_id = payload.get("sub")
        if not session_id or not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    await db.sessions.update_one(
        {"_id": session_id, "user_id": ObjectId(user_id)},
        {"$set": {"is_revoked": True, "revoked_at": datetime.utcnow()}},
    )
    return {"message": "Logged out successfully"}
