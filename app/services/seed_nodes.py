import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal
from app.models.node import Node
from app.core.config import settings
import os

PDF_PATH = os.path.join(os.path.dirname(__file__), "../../수학_교육과정.pdf")

async def seed_nodes():
    """
    교육부 PDF를 Upstage Document Digitization API로 파싱하여
    '핵심 개념 → 내용 요소' 구조의 노드를 DB에 저장
    """
    async with httpx.AsyncClient() as client:
        # PDF 파일이 열려있는지 확인
        if not os.path.exists(PDF_PATH):
            print(f"Error: PDF file not found at {PDF_PATH}")
            return

        with open(PDF_PATH, "rb") as f:
            files = {"document": f}
            data = {"model": "document-parse"}
            headers = {"Authorization": f"Bearer {settings.UPSTAGE_API_KEY}"}

            res = await client.post(
                "https://api.upstage.ai/v1/document-digitization",
                headers=headers,
                files=files,
                data=data,
            )
            res.raise_for_status()
            parsed = res.json()

    # 파싱된 JSON에서 content 추출 (API 응답 구조에 따라 키가 다를 수 있음)
    # 예시 응답을 바탕으로 'text' 또는 다른 적절한 키를 사용해야 할 수 있습니다.
    # 여기서는 응답에 'text'가 있고, 그 안에 필요한 정보가 있다고 가정합니다.
    # 실제 응답 구조를 확인하고 이 부분을 조정해야 합니다.
    
    # 예시: parsed = {"chunks": [{"properties": ..., "text": "수학I\n핵심 개념: 다항함수의 미분법\n내용 요소: 접선의 방정식"}, ...]}
    # 아래 로직은 `parsed.get("content", [])`가 기존처럼 동작한다고 가정합니다.
    # 실제로는 `parsed.get("chunks")` 등을 순회하며 `text`를 파싱해야 할 수 있습니다.
    
    contents = parsed.get("content", []) # 이 부분은 실제 API 응답에 맞춰 수정 필요

    async with SessionLocal() as db:
        for item in contents:
            subject = item.get("subject")
            concept = item.get("concept")
            element = item.get("element")

            if not subject or not concept or not element:
                continue

            node = Node(subject=subject, concept=concept, element=element)
            db.add(node)

        await db.commit()