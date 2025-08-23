FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

# Alembic으로 마이그레이션 후 서버 실행
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
