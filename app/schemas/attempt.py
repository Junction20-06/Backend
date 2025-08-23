from pydantic import BaseModel

class AttemptCreate(BaseModel):
    profile_id: int
    node_id: int
    question_id: str
    is_correct: bool
    difficulty: str # API 요청 시 난이도도 함께 받음

class AttemptOut(BaseModel):
    id: int
    profile_id: int
    node_id: int
    question_id: str
    is_correct: bool
    difficulty: str # 응답에도 난이도를 포함

    class Config:
        from_attributes = True