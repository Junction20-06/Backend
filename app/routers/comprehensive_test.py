import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.node import Node, ProfileNodeDetail
from app.schemas.node import NodeStatus
from app.services.solar_ai import generate_question

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/{profile_id}")
async def get_comprehensive_test_question(profile_id: int, db: AsyncSession = Depends(get_db)):
    """
    사용자 맞춤형 종합 테스트 문제를 1개 생성합니다.
    - 'weak' 상태 노드가 있으면 해당 노드 중 하나를 랜덤 선택하여 문제를 생성합니다.
    - 'weak' 노드가 없으면, 전체 노드 중 하나를 랜덤 선택하여 문제를 생성합니다.
    - 문제의 난이도는 '중'으로 고정됩니다.
    """
    
    # 1. 사용자의 'weak' 상태인 노드 ID 목록을 가져옵니다.
    weak_nodes_query = select(Node).join(ProfileNodeDetail).where(
        ProfileNodeDetail.profile_id == profile_id,
        ProfileNodeDetail.status == NodeStatus.weak
    )
    weak_nodes_result = await db.execute(weak_nodes_query)
    target_nodes = weak_nodes_result.scalars().all()

    # 2. 'weak' 노드가 없으면 전체 노드에서 랜덤으로 하나 선택
    if not target_nodes:
        all_nodes_result = await db.execute(select(Node))
        all_nodes = all_nodes_result.scalars().all()
        
        if not all_nodes:
            raise HTTPException(status_code=404, detail="No nodes available to generate a test.")
        
        target_nodes = all_nodes

    # 3. 대상 노드 중에서 하나를 랜덤으로 선택
    selected_node = random.choice(target_nodes)

    # 4. 선택된 노드로 문제 생성 (난이도 '중' 고정)
    question = await generate_question(selected_node.concept, selected_node.element, "중")
    
    return question