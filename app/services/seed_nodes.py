import httpx
import os
import re
import asyncio
import json
from sqlalchemy.dialects.postgresql import insert
from app.core.database import SessionLocal
from app.models.node import Node
from app.core.config import settings

PDF_PATH = os.path.join(os.path.dirname(__file__), "../../수학_교육과정.pdf")

TARGET_SUBJECTS = ["수학", "수학Ⅰ", "수학Ⅱ", "미적분", "확률과 통계", "기하"]

def parse_target_nodes(elements: list):
    subjects_tree = []

    for element in elements:
        if element.get("type") != "table":
            continue

        html_content = element.get("content", {}).get("html", "")
        if not html_content:
            continue

        rows = re.findall(r'<tr.*?>(.*?)</tr>', html_content, re.DOTALL)

        for row in rows[1:]:
            cells = re.findall(r'<td.*?>(.*?)</td>', row, re.DOTALL)

            def clean_text(text):
                return re.sub(r'<[^>]+>', '', text).strip()

            if len(cells) < 4:
                continue

            subject_text = clean_text(cells[0])
            if subject_text not in TARGET_SUBJECTS:
                continue  # 🎯 타겟 과목만 추출

            concept = clean_text(cells[1])
            elements_text = clean_text(cells[3])

            if not concept or not elements_text:
                continue

            element_list = [e.strip() for e in elements_text.split('•') if e.strip()]

            # 과목 트리 찾기
            subject_node = next((s for s in subjects_tree if s["subject"] == subject_text), None)
            if not subject_node:
                subject_node = {"subject": subject_text, "concepts": []}
                subjects_tree.append(subject_node)

            subject_node["concepts"].append({
                "concept": concept,
                "elements": element_list
            })

    return subjects_tree

async def seed_nodes():
    if not os.path.exists(PDF_PATH):
        print(f"Error: PDF file not found at {PDF_PATH}")
        return

    API_URL = "https://api.upstage.ai/v1/document-digitization"
    headers = {"Authorization": f"Bearer {settings.UPSTAGE_API_KEY}"}

    job_id = None
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            with open(PDF_PATH, "rb") as f:
                files = {"document": (os.path.basename(PDF_PATH), f.read(), "application/pdf")}
                data = {"model": "document-parse", "ocr": "auto"}
                params = {"async": "true"}

                response = await client.post(API_URL, headers=headers, files=files, data=data, params=params)
                if response.status_code != 202:
                    print(f"작업 요청 실패: {response.status_code} - {response.text}")
                    return

                result = response.json()
                job_id = result.get("job_id")
                if not job_id:
                    print("API 응답에서 job_id 없음")
                    return

        except Exception as e:
            print(f"작업 요청 중 오류: {e}")
            return

        ASYNC_RESULT_URL = f"https://api.upstage.ai/v1/document-digitization/jobs/{job_id}"

        while True:
            try:
                await asyncio.sleep(20)
                response = await client.get(ASYNC_RESULT_URL, headers=headers)
                response.raise_for_status()
                status_data = response.json()
                status = status_data.get("status")

                if status == "completed":
                    parsed_data = status_data.get("result", {})
                    break
                elif status == "failed":
                    print("작업 실패:", status_data.get("error"))
                    return

            except Exception as e:
                print(f"상태 확인 오류: {e}")
                return

    elements = parsed_data.get("elements")
    if not elements:
        print("구조화 데이터 없음")
        return

    nodes_to_add = parse_target_nodes(elements)
    if not nodes_to_add:
        print("노드 없음")
        return

    async with SessionLocal() as db:
        # await db.execute(Node.__table__.delete())
        # await db.execute(insert(Node), nodes_to_add)
        await db.commit()
        print(f"총 {len(nodes_to_add)}개의 노드를 저장했습니다.")
