from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routers import posts, applications, post_questions, auth
from database import Base, engine
from datetime import datetime
from fastapi import APIRouter

# Rate Limiter 설정
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="JOBA Backend API",
    description="JOBA 프로젝트 백엔드 API",
    version="1.0.0"
)

# Rate Limiter를 앱에 추가
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 로컬 개발용
        "http://localhost:3000",  # 다른 로컬 포트도 추가
        "http://localhost:8080",  # 추가 로컬 포트
        "https://ssajava-front.vercel.app",  # 프론트엔드 배포 URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 버전 관리 - v1 네임스페이스
# v1 API 라우터
v1_router = APIRouter(prefix="/v1")

# 기존 라우터들을 v1 네임스페이스에 포함
v1_router.include_router(posts.router, tags=["posts"])
v1_router.include_router(applications.router, tags=["applications"])
v1_router.include_router(post_questions.router, tags=["post_questions"])
# auth.router를 맨 마지막에 등록
v1_router.include_router(auth.router, tags=["auth"])

# 메인 앱에 v1 라우터 포함
app.include_router(v1_router)

# DB 테이블 생성
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# 서버 슬립 방지를 위한 핑 엔드포인트
@app.get("/ping")
@app.head("/ping")
@limiter.limit("100/minute")
def ping(request: Request):
    return {"message": "pong"}

# 헬스체크 엔드포인트
@app.get("/health")
@app.head("/health")
@limiter.limit("50/minute")
def health_check(request: Request):
    return {"status": "healthy", "version": "1.0.0"}