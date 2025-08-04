from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
from sqlalchemy.dialects.postgresql import JSONB

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    image_url = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    recruitment_field = Column(String(50), nullable=False)
    recruitment_headcount = Column(String(50), nullable=False)
    school_specific = Column(Boolean, nullable=False)
    target_school_name = Column(String(100), nullable=True)
    deadline = Column(DateTime, nullable=False)
    external_link = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    views = Column(Integer, nullable=False, default=0)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    applicant_id = Column(Integer, nullable=False)
    motivation = Column(Text, nullable=False)
    most_memorable_project = Column(Text, nullable=False)
    portfolio_pdf_url = Column(String(255), nullable=False)
    meeting_available_time = Column(JSONB, nullable=False)
    aspirations = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    status = Column(String(20), nullable=False, default="제출됨")

    # 중복 지원 방지 (같은 applicant_id가 같은 post_id에 중복 지원 불가)
    __table_args__ = (
        UniqueConstraint('applicant_id', 'post_id', name='unique_applicant_post'),
    )

# 사용자
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    kakao_id = Column(String, unique=True, nullable=True)
    naver_id = Column(String, unique=True, nullable=True)
    google_id = Column(String, unique=True, nullable=True)

    email = Column(String, unique=True, nullable=True)

    # 가입하기에서 받는 필드
    nickname = Column(String, nullable=True)
    track = Column(String, nullable=True)
    school = Column(String, nullable=True)
    portfolio_url = Column(Text, nullable=True)

    is_onboarded = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# DB 세션 의존성
from typing import Generator

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 