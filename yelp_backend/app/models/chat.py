from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    message = Column(Text, nullable=False)
    role = Column(Enum('user', 'assistant'), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="chat_history")
