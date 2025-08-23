# Backend/app/routers/attempts.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import SessionLocal
from app.models.attempt import Attempt
from app.models.node import Node, NodeStatus
from app.models.node import ProfileNodeDetail # 새로 추가한 모델 import
from app.schemas.attempt import AttemptCreate, AttemptOut

router = APIRouter()

# --- 점수 계산 정책 ---
SCORE_POINTS = {"하": 5, "중": 10, "상": 15}
# --------------------

# --- 노드 상태 결정 점수 기준 ---
STATUS_THRESHOLDS = {
    NodeStatus.strong: 70,
    NodeStatus.neutral: 30,
    NodeStatus.weak: 0 
}
# ---------------------------

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=AttemptOut)
async def record_attempt(data: AttemptCreate, db: AsyncSession = Depends(get_db)):
    # 1. 사용자-노드 상세 정보(점수) 가져오기
    detail_result = await db.execute(
        select(ProfileNodeDetail).where(
            ProfileNodeDetail.profile_id == data.profile_id,
            ProfileNodeDetail.node_id == data.node_id
        )
    )
    detail = detail_result.scalar_one_or_none()
    if not detail:
        raise HTTPException(status_code=404, detail="ProfileNodeDetail not found. Please request a question first.")

    # 2. 점수 계산 및 업데이트
    points = SCORE_POINTS.get(data.difficulty, 10)
    score_change = points if data.is_correct else -points
    detail.score += score_change
    
    # 3. 노드 상태 업데이트 로직
    new_score = detail.score
    new_status = NodeStatus.weak # 기본값
    if new_score >= STATUS_THRESHOLDS[NodeStatus.strong]:
        new_status = NodeStatus.strong
    elif new_score >= STATUS_THRESHOLDS[NodeStatus.neutral]:
        new_status = NodeStatus.neutral
        
    await db.execute(
        update(Node)
        .where(Node.id == data.node_id)
        .values(status=new_status)
    )

    # 4. 답변 시도 기록
    attempt = Attempt(**data.model_dump())
    db.add(attempt)
    
    await db.commit()
    await db.refresh(attempt)
    return attempt

@router.get("/{profile_id}", response_model=list[AttemptOut])
async def get_attempts(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Attempt).where(Attempt.profile_id == profile_id))
    return result.scalars().all()