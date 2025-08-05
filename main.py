from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import posts, applications, post_questions, auth
from database import Base, engine
from datetime import datetime

app = FastAPI()

# CORS 설정
origins = [
    "*",  # 개발 시 전체 허용, 배포 시 도메인 제한 권장
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(posts.router)
app.include_router(applications.router)
app.include_router(post_questions.router)
app.include_router(auth.router)

# DB 테이블 생성
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# 서버 슬립 방지를 위한 핑 엔드포인트
@app.get("/ping")
@app.head("/ping")
def ping():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "Server is running"
    }

# 헬스체크 엔드포인트
@app.get("/health")
@app.head("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "joba-backend"
    }