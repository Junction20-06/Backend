from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.attempt import Attempt
from app.models.node import Node
from app.schemas.report import ReportOut, NodeReport

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/{profile_id}", response_model=ReportOut)
async def generate_report(profile_id: int, db: AsyncSession = Depends(get_db)):
    """학습 기록 기반 JSON 리포트 (간단 버전)"""
    attempts = (await db.execute(select(Attempt).where(Attempt.profile_id == profile_id))).scalars().all()
    nodes = (await db.execute(select(Node))).scalars().all()

    strengths, weaknesses, neutrals = [], [], []

    for node in nodes:
        node_attempts = [a for a in attempts if a.node_id == node.id]
        if not node_attempts:
            continue
        accuracy = sum(1 for a in node_attempts if a.is_correct) / len(node_attempts)
        if accuracy > 0.8:
            strengths.append(NodeReport(node_id=node.id, status="strong"))
        elif accuracy < 0.5:
            weaknesses.append(NodeReport(node_id=node.id, status="weak"))
        else:
            neutrals.append(NodeReport(node_id=node.id, status="neutral"))

    return ReportOut(strengths=strengths, weaknesses=weaknesses, neutrals=neutrals)
