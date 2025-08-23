from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, String, func
from app.core.database import Base

class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    node_id = Column(Integer, ForeignKey("nodes.id"))
    question_id = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    difficulty = Column(String, nullable=False) # 난이도('하', '중', '상') 기록