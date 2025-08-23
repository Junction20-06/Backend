from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.attempt import Attempt
from app.schemas.attempt import AttemptCreate, AttemptOut

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=AttemptOut)
async def record_attempt(data: AttemptCreate, db: AsyncSession = Depends(get_db)):
    attempt = Attempt(
        profile_id=data.profile_id,
        node_id=data.node_id,
        question_id=data.question_id,
        is_correct=data.is_correct,
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    return attempt

@router.get("/{profile_id}", response_model=list[AttemptOut])
async def get_attempts(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Attempt).where(Attempt.profile_id == profile_id))
    return result.scalars().all()

