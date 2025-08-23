import httpx
import os
import re
import asyncio
import json
from sqlalchemy.dialects.postgresql import insert
from app.core.database import SessionLocal
from app.models.node import Node
from app.core.config import settings

# PDF 파일 경로를 정확하게 지정합니다.
PDF_PATH = os.path.join(os.path.dirname(__file__), "../../수학_교육과정.pdf")

def parse_nodes_tree_and_rows(elements: list, target_subjects: set | None = None):
    """
    HTML 표를 파싱해 트리와 flat row를 동시에 생성
    - 트리: {subject: {concept: [elements...]}}
    - rows: [{"subject": ..., "concept": ..., "element": ...}, ...]
    target_subjects에 {"확률과 통계"} 처럼 넣으면 해당 영역만 추출
    """
    def clean_text(text: str) -> str:
        # 태그 제거 + 공백 정리
        t = re.sub(r'<[^>]+>', '', text or '').strip()
        # 연속 공백/개행 정리
        t = re.sub(r'[ \t\r\f\v]+', ' ', t)
        t = re.sub(r'\n+', '\n', t)
        return t

    def split_items(s: str) -> list[str]:
        s = s.strip()
        if not s:
            return []
        # • 가 있으면 우선적으로 사용, 없으면 개행/세미콜론/중점/하이픈도 분해 시도
        if '•' in s:
            parts = s.split('•')
        else:
            parts = re.split(r'[\n;·\-]+', s)
        return [p.strip() for p in parts if p and p.strip()]

    tree: dict[str, dict[str, list[str]]] = {}
    rows: list[dict[str, str]] = []

    print("HTML 테이블 파싱을 시작합니다...")

    for element in elements:
        if element.get("type") != "table":
            continue

        html = element.get("content", {}).get("html", "")
        if not html:
            continue

        # 행/셀 추출 (th/td 모두 허용)
        tr_list = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
        if not tr_list:
            continue

        # 헤더 파악
        header_cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr_list[0], re.DOTALL | re.IGNORECASE)
        headers = [clean_text(c) for c in header_cells]
        header_join = " ".join(headers)

        # 우리가 원하는 표인지 확인(헤더에 핵심 단어가 들어가는지)
        if not (re.search(r'영역', header_join) and re.search(r'핵심\s*개념', header_join) and re.search(r'내용\s*요소', header_join)):
            continue

        # 열 인덱스 검출 (못 찾으면 안전한 기본값으로)
        def find_idx(keywords: list[str], default: int) -> int:
            for i, h in enumerate(headers):
                if any(kw in h for kw in keywords):
                    return i
            return default

        subject_idx = find_idx(["영역"], 0)
        concept_idx = find_idx(["핵심 개념", "핵심개념"], 1)
        element_idx = find_idx(["내용 요소", "내용요소"], 3)

        current_subject = None

        # 데이터 행 순회
        for row_html in tr_list[1:]:
            cells_html = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row_html, re.DOTALL | re.IGNORECASE)
            # 일부 표는 rowspan 때문에 셀 수가 들쭉날쭉
            cells = [clean_text(c) for c in cells_html]

            # subject 유지(행 병합 보정)
            if len(cells) > subject_idx and cells[subject_idx]:
                current_subject = cells[subject_idx]

            if not current_subject:
                continue

            # 영역 필터링
            if target_subjects and current_subject not in target_subjects:
                continue

            # 개념/내용요소
            concept = cells[concept_idx] if len(cells) > concept_idx else ""
            elements_text = cells[element_idx] if len(cells) > element_idx else ""
            if not concept or not elements_text:
                continue

            item_list = split_items(elements_text)
            if not item_list:
                continue

            # 트리 반영
            tree.setdefault(current_subject, {}).setdefault(concept, [])
            # 중복 방지
            existed = set(tree[current_subject][concept])
            for it in item_list:
                if it not in existed:
                    tree[current_subject][concept].append(it)
                    existed.add(it)
                    rows.append({
                        "subject": current_subject,
                        "concept": concept,
                        "element": it
                    })

    print(f"파싱 완료: subjects={len(tree)}개, rows={len(rows)}건")
    return tree, rows


async def seed_nodes():
    """
    (비동기 API 사용 - 최종 수정)
    교육부 PDF를 Upstage Document Parse API로 파싱하여
    '핵심 개념 → 내용 요소' 구조의 노드를 DB에 저장
    """
    if not os.path.exists(PDF_PATH):
        print(f"Error: PDF file not found at {PDF_PATH}")
        return

    API_URL = "https://api.upstage.ai/v1/document-digitization"
    headers = {"Authorization": f"Bearer {settings.UPSTAGE_API_KEY}"}
    job_id = None

    async with httpx.AsyncClient(timeout=None) as client:
        # 1. 작업 시작 요청
        try:
            with open(PDF_PATH, "rb") as f:
                # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ 최종 수정된 요청 형식 ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
                files = {"document": (os.path.basename(PDF_PATH), f.read(), "application/pdf")}
                data = {"model": "document-parse", "ocr": "auto"}
                params = {"async": "true"}
                # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

                print("Upstage 비동기 API에 PDF 분석 작업을 요청합니다...")
                response = await client.post(API_URL, headers=headers, files=files, data=data, params=params)
                
                # 요청 실패 시 응답 내용 출력 후 종료
                if response.status_code != 202: # 비동기 작업 시작 성공 코드는 202 Accepted 입니다.
                    print(f"작업 요청 실패: {response.status_code} - {response.text}")
                    return

                result = response.json()
                job_id = result.get("job_id")
                
                if not job_id:
                    print("API 응답에서 job_id를 찾을 수 없습니다.")
                    print("--- 전체 응답 ---")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    return

                print(f"작업 요청 성공. Job ID: {job_id}")

        except httpx.HTTPStatusError as e:
            print(f"작업 요청 실패: {e.response.status_code} - {e.response.text}")
            return
        except Exception as e:
            print(f"작업 요청 중 알 수 없는 오류 발생: {e}")
            return

        # 2. 작업 완료까지 폴링
        ASYNC_RESULT_URL = f"https://api.upstage.ai/v1/document-digitization/jobs/{job_id}"
        
        while True:
            try:
                await asyncio.sleep(20)
                print("작업 상태를 확인합니다...")
                response = await client.get(ASYNC_RESULT_URL, headers=headers)
                response.raise_for_status()
                status_data = response.json()
                status = status_data.get("status")
                
                print(f"현재 상태: {status}")
                
                if status == "completed":
                    print("작업 완료! 결과 처리를 시작합니다.")
                    parsed_data = status_data.get("result", {})
                    break
                elif status == "failed":
                    print("작업 실패:", status_data.get("error"))
                    return

            except httpx.HTTPStatusError as e:
                print(f"상태 확인 API 요청 실패: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                print(f"상태 확인 중 알 수 없는 오류 발생: {e}")
                return

    # 3. 결과 처리 및 DB 저장
    elements = parsed_data.get("elements")
    if not elements:
        print("최종 결과에서 'elements'를 찾을 수 없습니다.")
        return

    # 원하는 영역만: {"확률과 통계"}  (여러 개면 집합에 추가)
    target_subjects = ["수학", "수학Ⅰ", "수학Ⅱ", "미적분", "확률과 통계", "기하"]
    tree, rows = parse_nodes_tree_and_rows(elements, target_subjects=target_subjects)

    if not rows:
        print("저장할 row 데이터가 없습니다. 파싱 조건을 확인해주세요.")
        return

    async with SessionLocal() as db:
        await db.execute(Node.__table__.delete())
        await db.execute(insert(Node), rows)   # rows는 [{"subject","concept","element"}...]
        await db.commit()
        print(f"총 {len(rows)}개의 노드를 성공적으로 저장했습니다.")
