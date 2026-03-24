from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    cuisines = Column(String(255))
    price_range = Column(String(10))
    location = Column(String(255))
    search_radius = Column(Integer)
    dietary_needs = Column(String(255))
    ambiance = Column(String(255))
    sort_preference = Column(String(50))

    user = relationship("User", back_populates="preferences")
