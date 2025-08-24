import os
import asyncio
import traceback
import json
import uuid
from crewai import Agent, Task, Crew, Process
from crewai.crews.crew_output import CrewOutput # CrewOutput 클래스를 import
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from app.core.config import settings

# --- Pydantic 모델 정의 ---
class MathQuestion(BaseModel):
    question: str = Field(description="문제의 전체 내용")
    choices: list[str] = Field(description="5지선다형 선택지 리스트. 주관식의 경우 빈 리스트.")
    answer: str = Field(description="정답. 객관식일 경우 정답 선택지 번호를 '2'와 같이 문자열로 제공.")
    explanation: str = Field(description="3줄 이내의 핵심 풀이 과정")

# --- LLM 설정 ---
llm = ChatOpenAI(
    model="solar-pro2",
    api_key=settings.UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1",
    request_timeout=120.0
)

# --- 단일 전문가 에이전트 정의 ---
question_generation_agent = Agent(
    role="고등학교 수학 문제 출제 AI",
    goal="주어진 모든 지시사항을 완벽하게 반영하여, 학생에게 제공할 단 하나의 수학 문제를 Pydantic JSON 객체 형식으로 생성한다.",
    backstory="당신은 대한민국 고등학교 교육과정을 완벽하게 이해하고 있으며, 복잡한 요구사항도 빠짐없이 반영하여 항상 정확한 JSON 형식으로만 결과물을 출력하는 AI 에이전트입니다. 당신의 출력물에는 어떠한 추가 설명이나 마크다운도 포함되지 않습니다.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# --- 단일 Task 정의 ---
def create_final_question_task(agent, concept: str, element: str, difficulty: str):
    # 난이도별 문제 유형 정의 (서술형 제외)
    if difficulty == "하":
        question_type_prompt = """- **문제 유형**: 필수 개념을 이해했는지 간단하게 확인할 수 있는 O/X 형식의 명제를 출제합니다. "choices"는 `["O", "X"]`여야 하고, "answer"는 `"O"` 또는 `"X"`여야 한다. """
    elif difficulty == "중":
        question_type_prompt = """- **문제 유형**: 기본적인 개념과 일반적인 응용력을 평가하는 5지선다형 객관식 문제를 출제합니다. "choices"는 반드시 "1.", "2.", "3.", "4.", "5." 형식의 문자열 5개를 포함해야 하고, "answer"는 정답 번호를 나타내는 '1', '2' 등의 문자열이어야 한다."""
    else: # difficulty == "상"
        question_type_prompt = """- **문제 유형**: 심화 개념을 활용해야 하는 응용 주관식 문제를 출제합니다. "choices"는 빈 리스트 `[]`여야 하고, "answer"는 정답(숫자 또는 간단한 식)을 담은 문자열이어야 한다. 긴 서술형 답안은 절대 생성하지 않는다."""

    # 모든 지시사항을 하나의 프롬프트에 통합
    return Task(
        description=f"""
            당신은 아래의 모든 규칙을 따라야 합니다. 최종 목표는 단 하나의 완벽한 JSON 객체를 생성하는 것입니다.
            다른 설명, 인사, 마크다운 코드 블록 없이 오직 JSON 객체만 출력해야 합니다.

            **[문제 생성 지시]**
            1. **개념**: {concept}
            2. **내용 요소**: {element}
            3. **난이도**: {difficulty}
            4. {question_type_prompt}

            **[매우 중요한 공통 출력 조건]**
            1. **LaTeX 절대 사용 금지**: `\\frac`, `\\sin` 등 백슬래시(\\)를 포함하는 모든 LaTeX 문법은 절대로 사용해서는 안 됩니다. 그리고 제곱근과 같은 내용을 표현할때에는 명령어가 아닌 기호(ex.'√ ')를 사용해야 합니다. 모든 수학 기호는 텍스트로만 표현해야 합니다. (올바른 예: x^2, 1/2, sqrt(x+2))
            2. **대한민국 고등학교 교육과정 준수**.
            3. **3줄 이내의 핵심 해설**을 'explanation'에 포함.
            4. **Pydantic 스키마 준수**: 최종 출력은 `MathQuestion` 모델과 정확히 일치해야 한다.
        """,
        expected_output="`MathQuestion` Pydantic 모델 스키마를 따르는, 다른 부가 설명이 전혀 없는 순수한 JSON 객체.",
        agent=agent,
        output_pydantic=MathQuestion
    )

# --- Crew 실행 로직 ---
def run_crew_sync(concept: str, element: str, difficulty: str):
    try:
        task = create_final_question_task(question_generation_agent, concept, element, difficulty)
        crew = Crew(
            agents=[question_generation_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        result = crew.kickoff()
        return result
    except Exception as e:
        traceback.print_exc()
        raise e

async def generate_question_crew(concept: str, element: str, difficulty: str):
    try:
        result = await asyncio.to_thread(
            run_crew_sync, concept, element, difficulty
        )

        if isinstance(result, CrewOutput):
            json_string = result.raw
            question_data = json.loads(json_string)
        else:
            question_data = result.model_dump() if isinstance(result, MathQuestion) else result


        question_data["question_id"] = str(uuid.uuid4())
        question_data["difficulty"] = difficulty
        return question_data
    except Exception as e:
        print(f"\n--- [CRITICAL_ERROR] An exception was caught in generate_question_crew ---\nError: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"An internal error occurred in the AI crew: {e}")