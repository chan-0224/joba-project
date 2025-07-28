from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import posts
from database import Base, engine

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

# DB 테이블 생성
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine) 