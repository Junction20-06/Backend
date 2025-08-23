# Backend/app/routers/question.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import SessionLocal
from app.services.solar_ai import generate_question
from app.models.node import Node
from app.models.node import ProfileNodeDetail  # 새로 추가한 모델 import

router = APIRouter()

# --- 난이도 및 점수 정책 설정 ---
DIFFICULTY_LEVELS = {
    "하": {"min": -100, "max": 29},
    "중": {"min": 30, "max": 69},
    "상": {"min": 70, "max": 1000}
}
# --------------------------------

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/{profile_id}/{node_id}")
async def get_question_by_difficulty(profile_id: int, node_id: int, db: AsyncSession = Depends(get_db)):
    """사용자 점수 기반, 난이도 조절 및 다음 레벨 점수 안내 기능이 포함된 문제 생성"""
    
    # 1. 노드 정보 가져오기
    node_result = await db.execute(select(Node).where(Node.id == node_id))
    node = node_result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # 2. 사용자-노드 상세 정보(점수) 가져오기 (없으면 생성)
    detail_result = await db.execute(
        select(ProfileNodeDetail).where(
            ProfileNodeDetail.profile_id == profile_id,
            ProfileNodeDetail.node_id == node_id
        )
    )
    detail = detail_result.scalar_one_or_none()

    if not detail:
        detail = ProfileNodeDetail(profile_id=profile_id, node_id=node_id, score=30)
        db.add(detail)
        await db.commit()
        await db.refresh(detail)

    # 3. 현재 점수를 기반으로 난이도 결정
    current_score = detail.score
    current_difficulty = "중" # 기본값
    for diff, levels in DIFFICULTY_LEVELS.items():
        if levels["min"] <= current_score <= levels["max"]:
            current_difficulty = diff
            break

    # 4. 다음 레벨까지 남은 점수 계산
    points_to_next_level = None
    if current_difficulty != "상":
        next_level_min_score = DIFFICULTY_LEVELS[
            "중" if current_difficulty == "하" else "상"
        ]["min"]
        points_to_next_level = max(0, next_level_min_score - current_score)

    # 5. 결정된 난이도로 AI에게 문제 생성 요청
    question = await generate_question(node.concept, node.element, current_difficulty)
    
    # 6. 추가 정보와 함께 응답 반환
    question["points_to_next_level"] = points_to_next_level
    question["current_difficulty"] = current_difficulty
    question["current_score"] = current_score
    
    return question