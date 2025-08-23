from fastapi import HTTPException
from openai import AsyncOpenAI
from app.core.config import settings
import json

# client를 전역으로 초기화하여 재사용
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
    try:
        # openai 라이브러리를 사용하여 API 호출
        chat_completion = await client.chat.completions.create(
            model="solar-pro2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            stream=False,
            # 타임아웃을 넉넉하게 30초로 설정
            timeout=30.0 
        )
        
        response_content = chat_completion.choices[0].message.content
        
        # AI가 반환한 내용이 유효한 JSON인지 파싱 시도
        return json.loads(response_content)

    # API 키가 잘못되었거나, Upstage 서버에서 인증 오류가 발생한 경우
    except Exception as e:
        # 실제 운영 환경에서는 print 대신 logging을 사용하는 것이 좋습니다.
        print(f"An unexpected error occurred: {e}") 
        raise HTTPException(
            status_code=503, 
            detail="AI 모델 서비스에 문제가 발생했습니다. 잠시 후 다시 시도해 주세요."
        )