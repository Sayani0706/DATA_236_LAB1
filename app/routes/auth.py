from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.auth import hash_password, verify_password, create_token
from pydantic import BaseModel, EmailStr

router = APIRouter()

class SignupData(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "user"
    restaurant_location: str = None

class LoginData(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(data: SignupData, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role=data.role,
        city=data.restaurant_location if data.role == "owner" else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "role": user.role}

@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "role": user.role}

# this endpoint is for swagger authorize button only
@router.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
