from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.node import Node
from app.schemas.node import NodeOut

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/nodes", response_model=list[NodeOut])
async def get_nodes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Node))
    return result.scalars().all()
