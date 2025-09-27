from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, func, ForeignKey, UniqueConstraint, Index, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import settings
from sqlalchemy.dialects.postgresql import JSONB

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)  # 소셜 ID 기반 user_id
    image_url = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    recruitment_field = Column(String(50), nullable=False, index=True)  # 인덱스 추가
    recruitment_headcount = Column(String(50), nullable=False)
    school_specific = Column(Boolean, nullable=False, index=True)  # 인덱스 추가
    target_school_name = Column(String(100), nullable=True)
    deadline = Column(DateTime, nullable=False, index=True)  # 인덱스 추가
    external_link = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)  # 인덱스 추가
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # 복합 인덱스 추가
    __table_args__ = (
        Index('idx_posts_user_created', 'user_id', 'created_at'),
        Index('idx_posts_field_deadline', 'recruitment_field', 'deadline'),
    )

class PostQuestion(Base):
    __tablename__ = "post_questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)  # 인덱스 추가
    question_type = Column(String(50), nullable=False, index=True)  # 인덱스 추가
    question_content = Column(Text, nullable=False)
    is_required = Column(Boolean, nullable=False, default=False, index=True)  # 인덱스 추가
    choices = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # 복합 인덱스 추가
    __table_args__ = (
        Index('idx_post_questions_post_type', 'post_id', 'question_type'),
        Index('idx_post_questions_post_required', 'post_id', 'is_required'),
    )

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)  # 인덱스 추가
    user_id = Column(String, nullable=False, index=True)  # 소셜 ID 기반 user_id (applicant_id → user_id로 통일)
    status = Column(String(50), nullable=False, default="제출됨", index=True)  # 인덱스 추가
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)  # 인덱스 추가
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # 중복 지원 방지 (같은 user_id가 같은 post_id에 중복 지원 불가)
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='unique_user_post'),
        Index('idx_applications_post_status', 'post_id', 'status'),
        Index('idx_applications_user_created', 'user_id', 'created_at'),
    )

class ApplicationAnswer(Base):
    __tablename__ = "application_answers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, index=True)  # 인덱스 추가
    post_question_id = Column(Integer, ForeignKey("post_questions.id"), nullable=False, index=True)  # 인덱스 추가
    answer_content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # 복합 인덱스 추가
    __table_args__ = (
        Index('idx_application_answers_application', 'application_id'),
        Index('idx_application_answers_question', 'post_question_id'),
    )

class ApplicationStatusLog(Base):
    __tablename__ = "application_status_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, index=True)
    previous_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    changed_by_user_id = Column(Integer, nullable=False, index=True)  # 상태를 변경한 사용자 ID
    change_reason = Column(Text, nullable=True)  # 변경 사유 (선택사항)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    # 복합 인덱스 추가
    __table_args__ = (
        Index('idx_status_logs_application_created', 'application_id', 'created_at'),
        Index('idx_status_logs_changed_by', 'changed_by_user_id', 'created_at'),
    )

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=True, unique=True, index=True)  # 소셜 ID 기반 user_id

    kakao_id = Column(String, unique=True, nullable=True, index=True)  # 인덱스 추가
    naver_id = Column(String, unique=True, nullable=True, index=True)  # 인덱스 추가
    google_id = Column(String, unique=True, nullable=True, index=True)  # 인덱스 추가

    email = Column(String, unique=True, nullable=True, index=True)  # 인덱스 추가

    # 온보딩에 필요한 정보들 (DB 컬럼명은 신 키로 매핑)
    nickname = Column('name', String, nullable=True, index=True)  # 인덱스 추가
    track = Column('field', String, nullable=True, index=True)  # 인덱스 추가
    school = Column('university', String, nullable=True, index=True)  # 인덱스 추가
    portfolio_url = Column('portfolio', Text, nullable=True)

    is_onboarded = Column(Boolean, nullable=False, default=False, index=True)  # 인덱스 추가

    created_at = Column(DateTime, server_default=func.now(), index=True)  # 인덱스 추가
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 프로필 관련 컬럼들 (직접 프로필에서 관리하는 요소들)
    avatar_url = Column(String(500))     # 프로필 사진 URL
    cover_url = Column(String(500))      # 커버 사진 URL
    timetable_url = Column(String(500)) # 시간표 이미지 URL

    careers = relationship("ProfileCareer", back_populates="user", cascade="all, delete-orphan")

    # 복합 인덱스 추가
    __table_args__ = (
        Index('idx_users_track_onboarded', 'field', 'is_onboarded'),
        Index('idx_users_school_onboarded', 'university', 'is_onboarded'),
    )


class ProfileCareer(Base):
    __tablename__ = "profile_careers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    year = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)

    user = relationship("User", back_populates="careers")


# DB 세션 의존성
from typing import Generator

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 