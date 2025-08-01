from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db, Post
from schemas import PostCreate, PostResponse, PostListResponse, RecruitmentFieldEnum, RecruitmentHeadcountEnum, PostOptionsResponse, SortEnum
from services.gcs_uploader import upload_file_to_gcs, generate_unique_blob_name
import logging
from sqlalchemy import or_, func
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.post("/posts", response_model=PostResponse)
def create_post(
    post_data: PostCreate = Depends(),
    image_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 이미지 파일 유효성 검사
    if not image_file.content_type or not image_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
    
    filename = image_file.filename or "uploaded_image"
    try:
        # GCS 업로드
        blob_name = generate_unique_blob_name(filename)
        image_url = upload_file_to_gcs(image_file, blob_name)
    except Exception as e:
        logging.error(f"GCS 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail="이미지 업로드에 실패했습니다.")
    
    # DB 저장
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
    sort: SortEnum = Query(SortEnum.LATEST, description="정렬 기준"),
    recruitment_field: Optional[RecruitmentFieldEnum] = Query(None, description="모집 분야"),
    recruitment_headcount: Optional[RecruitmentHeadcountEnum] = Query(None, description="모집 인원"),
    school_name: Optional[str] = Query(None, description="학교 이름"),
    deadline_before: Optional[datetime] = Query(None, description="모집 마감일 이전"),
    q: Optional[str] = Query(None, description="검색 키워드"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지당 공고 개수")
):
    query = db.query(Post)
    
    # 필터링
    if recruitment_field:
        query = query.filter(Post.recruitment_field == recruitment_field.value)
    if recruitment_headcount:
        query = query.filter(Post.recruitment_headcount == recruitment_headcount.value)
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
    
    # 총 개수
    total_count = query.count()
    
    # 정렬
    if sort == SortEnum.LATEST:
        query = query.order_by(Post.created_at.desc())
    elif sort == SortEnum.POPULAR:
        query = query.order_by(Post.views.desc())
    elif sort == SortEnum.RANDOM:
        query = query.order_by(func.random())
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 정렬 방식입니다.")
    
    # 페이지네이션
    offset = (page - 1) * size
    posts = query.offset(offset).limit(size).all()
    
    # 응답 변환
    post_responses = [PostResponse.model_validate(post) for post in posts]
    return PostListResponse(total_count=total_count, posts=post_responses)

@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post_detail(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="공고를 찾을 수 없습니다.")
    return PostResponse.model_validate(post)

@router.get("/posts/options", response_model=PostOptionsResponse)
def get_post_options():
    """
    공고 작성 시 선택 가능한 모집 분야 및 모집 인원 목록을 반환합니다.
    """
    recruitment_fields = [e.value for e in RecruitmentFieldEnum]
    recruitment_headcounts = [e.value for e in RecruitmentHeadcountEnum]
    return PostOptionsResponse(
        recruitment_fields=recruitment_fields,
        recruitment_headcounts=recruitment_headcounts
    ) 