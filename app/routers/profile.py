from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileOut

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=ProfileOut)
async def create_profile(profile: ProfileCreate, db: AsyncSession = Depends(get_db)):
    new_profile = Profile(nickname=profile.nickname, age=profile.age)
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    return new_profile

@router.get("/{profile_id}", response_model=ProfileOut)
async def get_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    return result.scalar_one()

