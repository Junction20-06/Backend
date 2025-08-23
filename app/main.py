from fastapi import FastAPI
from app.routers import profile, graph, question, attempts, report, admin

app = FastAPI(title="나만의 AI 선생님")

# 라우터 등록
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(graph.router, prefix="/graph", tags=["graph"])
app.include_router(question.router, prefix="/question", tags=["question"])
app.include_router(attempts.router, prefix="/attempts", tags=["attempts"])
app.include_router(report.router, prefix="/report", tags=["report"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
