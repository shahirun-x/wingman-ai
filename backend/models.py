from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database import Base

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    mood = Column(String, default="neutral")
    created_at = Column(DateTime(timezone=True), server_default=func.now())