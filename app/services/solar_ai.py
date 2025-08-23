from openai import AsyncOpenAI # ✅ AsyncOpenAI 사용
from app.core.config import settings

# ✅ client를 전역으로 초기화하여 재사용
client = AsyncOpenAI(
    api_key=settings.UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1"
)

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
    # ✅ openai 라이브러리를 사용하여 API 호출
    chat_completion = await client.chat.completions.create(
        model="solar-1-mini", # 범용 모델명으로 수정 (solar-pro2는 특정 모델일 수 있음)
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"}, # JSON 출력 형식 지정
        stream=False # 스트리밍 없이 한번에 응답 받기
    )
    
    # JSON 문자열을 파싱할 필요 없이 바로 dict 객체로 반환
    import json
    return json.loads(chat_completion.choices[0].message.content)