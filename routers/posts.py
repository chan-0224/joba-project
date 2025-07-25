from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db, Post
from schemas import PostCreate, PostResponse, PostListResponse
from services.gcs_uploader import upload_file_to_gcs, generate_unique_blob_name
import logging
from sqlalchemy import or_
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.post("/posts", response_model=PostResponse)
def create_post(
    post_data: PostCreate = Depends(),
    image_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. 이미지 파일 유효성 검사 (content_type, filename None 방지)
    if not image_file.content_type or not image_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
    filename = image_file.filename or "uploaded_image"
    try:
        # 2. GCS 업로드
        blob_name = generate_unique_blob_name(filename)
        image_url = upload_file_to_gcs(image_file, blob_name)
    except Exception as e:
        logging.error(f"GCS 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail="이미지 업로드에 실패했습니다.")
    # 3. DB 저장
    try:
        post = Post(
            user_id=post_data.user_id,
            image_url=image_url,
            title=post_data.title,
            description=post_data.description,
            recruitment_field=post_data.recruitment_field,
            recruitment_headcount=post_data.recruitment_headcount,
            school_specific=post_data.school_specific,
            target_school_name=post_data.target_school_name,
            deadline=post_data.deadline,
            external_link=post_data.external_link,
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
    except Exception as e:
        db.rollback()
        logging.error(f"DB 저장 실패: {e}")
        raise HTTPException(status_code=500, detail="공고 저장에 실패했습니다.")

@router.get("/posts", response_model=PostListResponse)
def list_posts(
    db: Session = Depends(get_db),
    sort: str = Query("latest", description="정렬 기준: 'latest'(최신순), 'popular'(인기순), 'oldest'(오래된 순)"),
    track: Optional[str] = Query(None, description="모집 분야 (예: 기획, 디자인)"),
    headcount: Optional[str] = Query(None, description="모집 인원 (예: 1~2인, 3~5인, 인원 미정)"),
    school_name: Optional[str] = Query(None, description="학교 이름 (target_school_name 또는 description/title에 포함)"),
    deadline_before: Optional[datetime] = Query(None, description="모집 마감일 이전 (YYYY-MM-DDTHH:MM:SS 형식)"),
    q: Optional[str] = Query(None, description="공고 제목 또는 설명에서 검색할 키워드"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지당 공고 개수")
):
    query = db.query(Post)
    # 필터링
    if track:
        query = query.filter(Post.recruitment_field == track)
    if headcount:
        query = query.filter(Post.recruitment_headcount == headcount)
    if school_name:
        query = query.filter(
            or_(
                Post.target_school_name == school_name,
                Post.description.contains(school_name),
                Post.title.contains(school_name)
            )
        )
    if deadline_before:
        query = query.filter(Post.deadline <= deadline_before)
    if q:
        query = query.filter(
            or_(
                Post.title.contains(q),
                Post.description.contains(q)
            )
        )
    # 총 개수 (페이지네이션 전)
    total_count = query.count()
    # 정렬
    if sort == "latest":
        query = query.order_by(Post.created_at.desc())
    elif sort == "popular":
        query = query.order_by(Post.views.desc())
    elif sort == "random":
        from sqlalchemy import func
        query = query.order_by(func.random())
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 정렬 방식입니다.")
    # 페이지네이션
    offset = (page - 1) * size
    posts = query.offset(offset).limit(size).all()
    # SQLAlchemy 모델을 Pydantic 모델로 변환
    post_responses = [PostResponse.model_validate(post) for post in posts]
    return PostListResponse(total_count=total_count, posts=post_responses)

@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post_detail(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse.model_validate(post) 