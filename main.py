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
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한해야 함
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 버전 관리 - v1 네임스페이스
# v1 API 라우터
v1_router = APIRouter(prefix="/v1")

# 기존 라우터들을 v1 네임스페이스에 포함
v1_router.include_router(posts.router, prefix="/posts", tags=["posts"])
v1_router.include_router(applications.router, prefix="/applications", tags=["applications"])
v1_router.include_router(post_questions.router, prefix="/posts", tags=["post_questions"])
v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 메인 앱에 v1 라우터 포함
app.include_router(v1_router)

# DB 테이블 생성
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# 서버 슬립 방지를 위한 핑 엔드포인트
@app.get("/ping")
@limiter.limit("100/minute")
def ping(request: Request):
    return {"message": "pong"}

# 헬스체크 엔드포인트
@app.get("/health")
@limiter.limit("50/minute")
def health_check(request: Request):
    return {"status": "healthy", "version": "1.0.0"}