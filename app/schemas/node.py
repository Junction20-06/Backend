from pydantic import BaseModel
from enum import Enum

class NodeStatus(str, Enum):
    not_started = "not_started"
    weak = "weak"
    neutral = "neutral"
    strong = "strong"

class NodeOut(BaseModel):
    id: int
    subject: str
    concept: str
    element: str
    status: NodeStatus

    class Config:
        from_attributes = True