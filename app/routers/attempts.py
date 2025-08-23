from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.attempt import Attempt
from app.models.node import ProfileNodeDetail # Node 모델은 더이상 직접 수정하지 않음
from app.models.node import NodeStatus
from app.schemas.attempt import AttemptCreate, AttemptOut

router = APIRouter()

SCORE_POINTS = {"하": 5, "중": 10, "상": 15}
STATUS_THRESHOLDS = {
    NodeStatus.strong: 70,
    NodeStatus.neutral: 30,
    NodeStatus.weak: 0 
}

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=AttemptOut)
async def record_attempt(data: AttemptCreate, db: AsyncSession = Depends(get_db)):
    detail_result = await db.execute(
        select(ProfileNodeDetail).where(
            ProfileNodeDetail.profile_id == data.profile_id,
            ProfileNodeDetail.node_id == data.node_id
        )
    )
    detail = detail_result.scalar_one_or_none()
    if not detail:
        raise HTTPException(status_code=404, detail="ProfileNodeDetail not found.")

    # 점수 계산
    points = SCORE_POINTS.get(data.difficulty, 10)
    score_change = points if data.is_correct else -points
    detail.score += score_change
    
    # ✨ 사용자별 상태(status) 업데이트
    new_score = detail.score
    if new_score >= STATUS_THRESHOLDS[NodeStatus.strong]:
        detail.status = NodeStatus.strong
    elif new_score >= STATUS_THRESHOLDS[NodeStatus.neutral]:
        detail.status = NodeStatus.neutral
    else:
        detail.status = NodeStatus.weak
        
    # 답변 시도 기록
    attempt = Attempt(**data.model_dump())
    db.add(attempt)
    
    await db.commit()
    await db.refresh(attempt)
    return attempt

@router.get("/{profile_id}", response_model=list[AttemptOut])
async def get_attempts(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Attempt).where(Attempt.profile_id == profile_id))
    return result.scalars().all()