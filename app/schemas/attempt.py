from pydantic import BaseModel

class AttemptCreate(BaseModel):
    profile_id: int
    node_id: int
    question_id: str
    is_correct: bool

class AttemptOut(BaseModel):
    id: int
    profile_id: int
    node_id: int
    question_id: str
    is_correct: bool

    class Config:
        from_attributes = True
