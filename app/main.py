from fastapi import FastAPI
import os

app = FastAPI(title="Hackathon API")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return {"hello": "world"}

# 로컬 테스트용: python app/main.py로 실행해도 동작
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))  # Railway가 PORT를 주입함
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)