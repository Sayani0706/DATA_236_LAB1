from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum('user', 'owner'), default='user')
    phone = Column(String(20))
    about_me = Column(String(1000))
    city = Column(String(100))
    state = Column(String(10))
    country = Column(String(100))
    languages = Column(String(255))
    gender = Column(String(20))
    profile_picture = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    reviews = relationship("Review", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    restaurants = relationship("Restaurant", back_populates="owner")
    chat_history = relationship("ChatHistory", back_populates="user")
