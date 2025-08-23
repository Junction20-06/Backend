from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base
import enum

class NodeStatus(enum.Enum):
    not_started = "not_started"
    weak = "weak"
    neutral = "neutral"
    strong = "strong"

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)    # 수학Ⅰ, 수학Ⅱ, ...
    concept = Column(String, nullable=False)    # 핵심 개념
    element = Column(String, nullable=False)    # 내용 요소
    status = Column(Enum(NodeStatus), default=NodeStatus.not_started)

