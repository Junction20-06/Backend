from fastapi import APIRouter
from app.services.solar_ai import generate_question

router = APIRouter()

@router.get("/{concept}/{element}")
async def get_question(concept: str, element: str):
    """개념 + 내용 요소 기반 문제 생성"""
    question = await generate_question(concept, element)
    return question
