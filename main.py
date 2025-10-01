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
from services.logging_stream import ensure_queue_handler, ensure_redis_handler

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
        "http://127.0.0.1:5173",  # 로컬 호스트 대안
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        # 명시적 고정 도메인(배포 본 도메인)
        "https://ssajava-front.vercel.app",
        "https://joba-frontend.onrender.com",
        "https://joba-frontend.vercel.app",
    ],
    # Vercel/Render 프리뷰 등 서브도메인 전체 허용
    allow_origin_regex=r"https://.*\.(vercel\.app|onrender\.com)$",
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

@app.on_event("startup")
def on_startup():
    try:
        # Ensure log handlers
        try:
            ensure_redis_handler()
        except Exception:
            pass
        try:
            ensure_queue_handler()
        except Exception:
            pass

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

            # posts.image_url 길이 확장 (255 -> 500)
            try:
                result = conn.execute(text("""
                    SELECT character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = 'posts' AND column_name = 'image_url'
                """))
                length_row = result.fetchone()
                current_len = length_row[0] if length_row else None
                if current_len is not None and current_len < 500:
                    print("posts.image_url 컬럼 길이 확장 중 (255 -> 500)...")
                    conn.execute(text("""
                        ALTER TABLE posts
                        ALTER COLUMN image_url TYPE VARCHAR(500)
                    """))
                    conn.commit()
                    print("✅ posts.image_url 컬럼 길이 확장 완료")
                else:
                    print("✅ posts.image_url 컬럼 길이 적절함")
            except Exception as e:
                print(f"⚠️ posts.image_url 컬럼 길이 점검/확장 중 경고: {e}")

            # posts.user_id 타입을 VARCHAR(100)으로 강제 (정수형 → 문자열로 전환)
            try:
                result = conn.execute(text("""
                    SELECT data_type
                    FROM information_schema.columns
                    WHERE table_name = 'posts' AND column_name = 'user_id'
                """))
                row = result.fetchone()
                current_type = row[0] if row else None
                if current_type and current_type != 'character varying':
                    print(f"posts.user_id 컬럼 타입 변경 중 ({current_type} -> VARCHAR(100))...")
                    conn.execute(text("""
                        ALTER TABLE posts
                        ALTER COLUMN user_id TYPE VARCHAR(100) USING user_id::text
                    """))
                    conn.commit()
                    print("✅ posts.user_id 컬럼 타입 변경 완료")
                else:
                    print("✅ posts.user_id 컬럼 타입 적절함")
            except Exception as e:
                print(f"⚠️ posts.user_id 컬럼 타입 점검/변경 중 경고: {e}")

            # posts.deadline 타입을 TIMESTAMP WITHOUT TIME ZONE으로 전환 (과거 DATE였던 스키마 호환)
            try:
                result = conn.execute(text("""
                    SELECT data_type
                    FROM information_schema.columns
                    WHERE table_name = 'posts' AND column_name = 'deadline'
                """))
                row = result.fetchone()
                current_type = row[0] if row else None
                if current_type and current_type != 'timestamp without time zone':
                    print(f"posts.deadline 컬럼 타입 변경 중 ({current_type} -> TIMESTAMP WITHOUT TIME ZONE)...")
                    conn.execute(text("""
                        ALTER TABLE posts
                        ALTER COLUMN deadline TYPE TIMESTAMP WITHOUT TIME ZONE USING deadline::timestamp
                    """))
                    conn.commit()
                    print("✅ posts.deadline 컬럼 타입 변경 완료")
                else:
                    print("✅ posts.deadline 컬럼 타입 적절함")
            except Exception as e:
                print(f"⚠️ posts.deadline 컬럼 타입 점검/변경 중 경고: {e}")
                
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