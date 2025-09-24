from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routers import posts, applications, post_questions, auth, profiles
from routers import logs as logs_router
from database import Base, engine
from datetime import datetime
from fastapi import APIRouter
from exceptions import JOBAException

# 데이터베이스 스키마 업데이트
Base.metadata.create_all(bind=engine)

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

# JOBA 예외 핸들러 추가
@app.exception_handler(JOBAException)
async def joba_exception_handler(request: Request, exc: JOBAException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 로컬 개발용
        "http://localhost:3000",  # 다른 로컬 포트도 추가
        "http://localhost:8080",  # 추가 로컬 포트
        "https://ssajava-front.vercel.app",  # 프론트엔드 배포 URL
        "https://ssajava-front.vercel.app/",  # 슬래시 포함 버전
        # Render 환경에서 추가할 수 있는 도메인들
        "https://joba-frontend.onrender.com",  # Render 프론트엔드 (예시)
        "https://joba-frontend.vercel.app",  # Vercel 프론트엔드 (예시)
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
v1_router.include_router(profiles.router, tags=["profile"])
# auth.router를 맨 마지막에 등록
v1_router.include_router(auth.router, tags=["auth"])
v1_router.include_router(logs_router.router, tags=["logs"])

# 메인 앱에 v1 라우터 포함
app.include_router(v1_router)

# DB 테이블 생성
@app.on_event("startup")
def on_startup():
    try:
        print("데이터베이스 스키마 업데이트 시작...")
        Base.metadata.create_all(bind=engine)
        print("✅ 데이터베이스 스키마 업데이트 완료")
        
        # user_id 컬럼이 없으면 추가 (PostgreSQL)
        from sqlalchemy import text
        with engine.connect() as conn:
            # users 테이블에 user_id 컬럼이 있는지 확인
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'user_id'
            """))
            
            if not result.fetchone():
                print("user_id 컬럼이 없습니다. 추가 중...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN user_id VARCHAR(100) UNIQUE
                """))
                conn.commit()
                print("✅ user_id 컬럼 추가 완료")
            else:
                print("✅ user_id 컬럼이 이미 존재합니다")
                
    except Exception as e:
        print(f"❌ 데이터베이스 스키마 업데이트 실패: {e}")
        # 에러가 발생해도 서버는 계속 실행

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