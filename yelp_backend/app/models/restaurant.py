from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(150), nullable=False)
    cuisine_type = Column(String(100))
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(10))
    zip = Column(String(20))
    description = Column(Text)
    hours = Column(String(255))
    contact = Column(String(100))
    pricing_tier = Column(String(10))
    amenities = Column(String(255))
    is_claimed = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="restaurants")
    photos = relationship("RestaurantPhoto", back_populates="restaurant")
    reviews = relationship("Review", back_populates="restaurant")
    favorites = relationship("Favorite", back_populates="restaurant")

class RestaurantPhoto(Base):
    __tablename__ = "restaurant_photos"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"))
    photo_url = Column(String(255), nullable=False)
    uploaded_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="photos")
