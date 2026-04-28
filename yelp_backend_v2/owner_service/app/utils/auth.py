from jose import JWTError, jwt
import bcrypt
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.mongodb import get_db
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def hash_password(password):
    if password is None:
        return None
    password_str = str(password)[:72]
    password_bytes = password_str.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain, hashed):
    plain_bytes = str(plain)[:72].encode("utf-8")
    hashed_bytes = hashed.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def create_token(data: dict):
    to_encode = data.copy()
    if "sid" not in to_encode:
        to_encode["sid"] = uuid4().hex
    if "exp" not in to_encode:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        session_id = payload.get("sid")
        if user_id is None or session_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        raise credentials_exception

    session = await db.sessions.find_one(
        {
            "_id": session_id,
            "user_id": user_obj_id,
            "is_revoked": {"$ne": True},
            "expires_at": {"$gt": datetime.utcnow()},
        }
    )
    if session is None:
        raise credentials_exception

    user = await db.users.find_one({"_id": user_obj_id})
    if user is None:
        raise credentials_exception
    return user


async def owner_only(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Owner access required")
    return current_user
