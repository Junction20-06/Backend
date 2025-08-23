from pydantic import BaseModel

class ProfileCreate(BaseModel):
    nickname: str
    age: int

class ProfileOut(BaseModel):
    id: int
    nickname: str
    age: int

    class Config:
        from_attributes = True

