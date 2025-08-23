import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal
from app.models.node import Node
from app.core.config import settings
import os

PDF_PATH = os.path.join(os.path.dirname(__file__), "../../수학_교육과정.pdf")

async def seed_nodes():
    """
    교육부 PDF를 Upstage Document Parse API로 파싱하여
    '핵심 개념 → 내용 요소' 구조의 노드를 DB에 저장
    """
    async with httpx.AsyncClient() as client:
        with open(PDF_PATH, "rb") as f:
            files = {"file": f}
            headers = {"Authorization": f"Bearer {settings.UPSTAGE_API_KEY}"}

            res = await client.post(
                "https://api.upstage.ai/v1/document/parse",
                headers=headers,
                files=files,
            )
            res.raise_for_status()
            parsed = res.json()

    # ✅ 파싱된 JSON 예시 구조 (단순화):
    # {
    #   "content": [
    #       {"subject": "수학Ⅰ", "concept": "다항함수의 미분법", "element": "접선의 방정식"},
    #       {"subject": "수학Ⅱ", "concept": "적분법", "element": "치환적분"},
    #       ...
    #   ]
    # }
    contents = parsed.get("content", [])

    async with SessionLocal() as db:
        for item in contents:
            subject = item.get("subject")
            concept = item.get("concept")
            element = item.get("element")

            if not subject or not concept or not element:
                continue  # 불완전한 항목 스킵

            node = Node(subject=subject, concept=concept, element=element)
            db.add(node)

        await db.commit()
