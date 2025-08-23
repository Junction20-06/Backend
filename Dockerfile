# 1. Python 베이스 이미지
FROM python:3.11-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. 시스템 패키지 설치 (PostgreSQL 드라이버 등)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. requirements.txt 복사 & 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 복사
COPY . .

# 6. 환경 변수 (Railway에서 주입됨)
ENV PORT=8000
EXPOSE 8000

# 7. 실행 (uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
