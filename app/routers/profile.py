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
    # 동일한 닉네임의 프로필이 이미 존재하는지 확인
    result = await db.execute(select(Profile).where(Profile.nickname == profile.nickname))
    existing_profile = result.scalar_one_or_none()

    if existing_profile:
        return existing_profile  # 프로필이 존재하면 기존 프로필 정보를 반환 (로그인)

    # 존재하지 않으면 새로운 프로필 생성
    new_profile = Profile(nickname=profile.nickname, age=profile.age)
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    return new_profile

@router.get("/{profile_id}", response_model=ProfileOut)
async def get_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    return result.scalar_one()