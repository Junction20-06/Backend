# Backend/app/routers/graph.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import SessionLocal
from app.models.node import Node, ProfileNodeDetail
from app.schemas.node import NodeOut

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

# ✨ profile_id를 받도록 URL 변경
@router.get("/nodes/{profile_id}", response_model=list[NodeOut])
async def get_nodes_for_user(profile_id: int, db: AsyncSession = Depends(get_db)):
    """특정 사용자의 학습 상태가 포함된 모든 노드 목록 조회"""
    
    # 1. 모든 노드 정보를 가져옴
    all_nodes_result = await db.execute(select(Node))
    all_nodes = all_nodes_result.scalars().all()
    
    # 2. 해당 사용자의 모든 학습 진행 상태를 가져옴
    details_result = await db.execute(
        select(ProfileNodeDetail).where(ProfileNodeDetail.profile_id == profile_id)
    )
    user_details_map = {detail.node_id: detail for detail in details_result.scalars()}

    # 3. 노드 정보와 사용자 상태를 조합하여 최종 응답 생성
    response_data = []
    for node in all_nodes:
        user_specific_detail = user_details_map.get(node.id)
        
        node_data = NodeOut(
            id=node.id,
            subject=node.subject,
            concept=node.concept,
            element=node.element,
            # 사용자의 진행 상태가 있으면 그것을, 없으면 'not_started'를 반환
            status=user_specific_detail.status if user_specific_detail else "not_started"
        )
        response_data.append(node_data)
        
    return response_data