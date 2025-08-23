from fastapi import HTTPException
from openai import AsyncOpenAI
from app.core.config import settings
import json
import uuid

client = AsyncOpenAI(
    api_key=settings.UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1"
)

async def generate_question(concept: str, element: str, difficulty: str):
    # --- 난이도별 문제 유형 정의 ---
    if difficulty == "하":
        question_type_prompt = """
- **문제 유형: O/X 문제**
- 필수 개념을 이해했는지 간단하게 확인할 수 있는 O/X 형식의 명제를 출제합니다.
- "question" 키에는 "다음 문장이 맞으면 O, 틀리면 X를 고르시오:" 라는 문장으로 시작해야 합니다.
- "choices" 키에는 `["O", "X"]` 두 개의 문자열만 포함해야 합니다.
- "answer" 키에는 정답인 `"O"` 또는 `"X"` 문자열을 제공합니다.
"""
    elif difficulty == "중":
        question_type_prompt = """
- **문제 유형: 객관식 문제**
- 기본적인 개념과 일반적인 응용력을 평가하는 5지선다형 객관식 문제를 출제합니다.
- "choices" 키에는 반드시 "1.", "2.", "3.", "4.", "5." 형식의 문자열 5개를 포함하는 리스트여야 합니다.
- "answer" 키에는 정답 선택지 번호에 해당하는 **숫자** (1, 2, 3, 4, 5 중 하나)를 제공합니다.
"""
    else: # difficulty == "상"
        question_type_prompt = """
- **문제 유형: 주관식 문제**
- 심화 개념을 활용해야 하는 응용 주관식 문제를 출제합니다.
- "choices" 키에는 빈 리스트 `[]`를 제공합니다.
- "answer" 키에는 정답(숫자 또는 간단한 식)을 **문자열** 형태로 제공합니다.
"""

    prompt = f"""
당신은 고등학교 수학 전문 선생님입니다.
다음 요청에 따라 학생에게 맞춤형 문제를 생성해 주세요.

**[문제 생성 지시]**
- 개념: {concept}
- 내용 요소: {element}
- **난이도: {difficulty}**

{question_type_prompt}

**[공통 출력 조건]**
1. **LaTeX 문법은 절대로 사용하지 마세요.** 모든 수학 기호와 분수는 텍스트로 표현해 주세요. (예: x^2, 1/2)
2. 문제는 반드시 대한민국 고등학교 과정 수준으로 작성합니다.
3. 상세하고 친절한 풀이 과정을 반드시 제공합니다.
4. 출력은 반드시 JSON 형식으로 작성하며, 다음 키를 포함해야 합니다:
   - "question" (문제 내용)
   - "choices" (선택지 리스트)
   - "answer" (정답)
   - "explanation" (풀이)
"""
    try:
        chat_completion = await client.chat.completions.create(
            model="solar-pro2",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            stream=False,
            timeout=30.0
        )
        
        response_content = chat_completion.choices[0].message.content
        question_data = json.loads(response_content)
        question_data["question_id"] = str(uuid.uuid4())
        question_data["difficulty"] = difficulty
        
        return question_data

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=503,
            detail="AI 모델 서비스에 문제가 발생했습니다. 잠시 후 다시 시도해 주세요."
        )