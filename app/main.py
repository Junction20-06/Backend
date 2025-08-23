from fastapi import FastAPI
from app.routers import profile, graph, question, attempts, report, admin, comprehensive_test # comprehensive_test 추가
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mentor AI")

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 등록
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(graph.router, prefix="/graph", tags=["graph"])
app.include_router(question.router, prefix="/question", tags=["question"])
app.include_router(attempts.router, prefix="/attempts", tags=["attempts"])
app.include_router(report.router, prefix="/report", tags=["report"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(comprehensive_test.router, prefix="/comprehensive", tags=["comprehensive"]) # 라우터 추가


@app.get("/")
async def root():
    return {"message": "Welcome to Mentor AI"}