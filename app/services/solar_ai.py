import httpx
from app.core.config import settings

async def generate_question(concept: str, element: str):
    prompt = f"""
당신은 고등학교 수학 선생님입니다.
다음 개념을 학습 중인 학생에게 맞춤형 문제를 생성해 주세요.

조건:
1. 문제는 고등학교 과정 수준으로 작성합니다.
2. 정답과 풀이 과정을 반드시 제공합니다.
3. 출력은 JSON 형식으로 작성합니다.
4. JSON 키는 반드시 포함해야 합니다:
   - "question"
   - "choices"
   - "answer"
   - "explanation"

개념: {concept}
내용 요소: {element}
"""
    url = "https://api.upstage.ai/v1/solar"
    headers = {"Authorization": f"Bearer {settings.UPSTAGE_API_KEY}"}
    data = {"input": prompt, "response_format": "json_object"}

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=data)
        res.raise_for_status()
        return res.json()
