"""
공고 관리 API 엔드포인트

이 모듈은 공고 생성, 조회, 목록 조회 기능을 제공합니다.
- 공고 생성: JWT 토큰 기반 인증 필요
- 공고 목록/상세 조회: 인증 불필요 (공개 API)
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db, Post, User, Application
from schemas import PostCreate, PostResponse, PostListResponse, RecruitmentFieldEnum, RecruitmentHeadcountEnum, SortEnum
from services.file_upload_service import FileUploadService
from routers.auth import get_current_user
import logging
from sqlalchemy import or_, func, select
from datetime import datetime
from typing import Optional

router = APIRouter()


@router.post("/posts", response_model=PostResponse)
async def create_post(
    post_data: PostCreate = Depends(),
    image_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    공고 생성
    
    이미지 파일과 함께 공고 정보를 생성합니다.
    
    Args:
        post_data: 공고 데이터 (제목, 설명, 모집 분야 등)
        image_file: 공고 이미지 파일
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션
        
    Returns:
        PostResponse: 생성된 공고 정보
        
    Raises:
        HTTPException: 이미지 파일 오류, 업로드 실패, DB 저장 실패
    """
    # 이미지 파일 유효성 검사
    if not image_file.content_type or not image_file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="이미지 파일만 업로드 가능합니다."
        )
    
    # GCS에 이미지 업로드
    image_url = await FileUploadService.upload_image(image_file)
    
    # DB에 공고 정보 저장
    try:
        # user_id는 DB에 저장된 값을 우선 사용하고, 없을 경우 provider 기반 생성으로 폴백
        user_id = getattr(current_user, "user_id", None)
        if not user_id:
            from services.user_service import get_user_id_from_user
            user_id = get_user_id_from_user(current_user)
        
        post = Post(
            user_id=user_id,
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
        # 상세 원인 파악을 위해 traceback 포함 로깅
        logging.error(f"DB 저장 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="공고 저장에 실패했습니다."
        )


@router.get("/posts", response_model=PostListResponse)
async def list_posts(
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
    """
    공고 목록 조회 (필터링, 정렬, 검색, 페이지네이션 지원)
    
    **인증 불필요** - 모든 사용자가 공고 목록을 조회할 수 있습니다.
    
    Args:
        db: 데이터베이스 세션
        sort: 정렬 기준 (최신순|인기순|랜덤순)
        recruitment_field: 모집 분야 필터 (프론트엔드, 백엔드, 기획, 디자인, 데이터 분석)
        recruitment_headcount: 모집 인원 필터 (1~2인, 3~5인, 6~10인, 인원미정)
        school_name: 학교명 검색 (title, description, target_school_name에서 검색)
        deadline_before: 마감일 이전 필터
        q: 검색 키워드 (제목, 설명에서 검색)
        page: 페이지 번호 (1부터 시작)
        size: 페이지당 공고 개수 (1~100)
        
    Returns:
        PostListResponse: 공고 목록 및 총 개수
        - 각 공고에 application_count, recruited_count, recruitment_status 포함
    """
    query = db.query(Post)
    
    # 필터링 적용
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
    
    # 총 개수 조회
    total_count = query.count()
    
    # 정렬 적용
    if sort == SortEnum.LATEST:
        query = query.order_by(Post.created_at.desc())
    elif sort == SortEnum.POPULAR:
        # 지원자 수를 계산하는 서브쿼리
        application_count = select(func.count(Application.id)).where(Application.post_id == Post.id).scalar_subquery()
        query = query.order_by(application_count.desc(), Post.created_at.desc())
    elif sort == SortEnum.RANDOM:
        query = query.order_by(func.random())
    
    # 페이지네이션 적용
    offset = (page - 1) * size
    posts = query.offset(offset).limit(size).all()
    
    # 각 공고의 지원자 수, 모집된 인원 수, 모집 상태를 계산해서 추가
    posts_with_count = []
    for post in posts:
        # 지원자 수 계산
        application_count = db.query(func.count(Application.id)).filter(Application.post_id == post.id).scalar()
        
        # 모집된 인원 수 계산 (합격자)
        recruited_count = db.query(func.count(Application.id)).filter(
            Application.post_id == post.id,
            Application.status == "합격"
        ).scalar()
        
        # 모집 상태 계산
        now = datetime.now()
        recruitment_status = "마감" if post.deadline < now else "모집중"
        
        # user_id 처리 (기존 Integer와 새로운 String 호환)
        user_id = post.user_id
        if isinstance(user_id, int):
            # 기존 Integer user_id를 String으로 변환
            user_id = str(user_id)
        
        post_dict = {
            "id": post.id,
            "user_id": user_id,
            "image_url": post.image_url,
            "title": post.title,
            "description": post.description,
            "recruitment_field": post.recruitment_field,
            "recruitment_headcount": post.recruitment_headcount,
            "school_specific": post.school_specific,
            "target_school_name": post.target_school_name,
            "deadline": post.deadline,
            "external_link": post.external_link,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "application_count": application_count or 0,
            "recruited_count": recruited_count or 0,
            "recruitment_status": recruitment_status
        }
        posts_with_count.append(post_dict)
    
    return PostListResponse(
        total_count=total_count,
        posts=posts_with_count
    )


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post_detail(
    post_id: int, 
    db: Session = Depends(get_db)
):
    """
    공고 상세 조회
    
    **인증 불필요** - 모든 사용자가 공고 상세 정보를 조회할 수 있습니다.
    
    Args:
        post_id: 조회할 공고 ID
        db: 데이터베이스 세션
        
    Returns:
        PostResponse: 공고 상세 정보
        - application_count: 지원자 수
        - recruited_count: 모집된 인원 수 (합격자 수)
        - recruitment_status: 모집 상태 ("모집중" 또는 "마감")
        - user_id: 문자열 형태로 변환된 사용자 ID
        
    Raises:
        HTTPException: 공고를 찾을 수 없음 (404)
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공고를 찾을 수 없습니다."
        )
    
    # 지원자 수 계산
    application_count = db.query(func.count(Application.id)).filter(Application.post_id == post.id).scalar()
    
    # 모집된 인원 수 계산 (합격자)
    recruited_count = db.query(func.count(Application.id)).filter(
        Application.post_id == post.id,
        Application.status == "합격"
    ).scalar()
    
    # 모집 상태 계산
    now = datetime.now()
    recruitment_status = "마감" if post.deadline < now else "모집중"
    
    # user_id 처리 (기존 Integer와 새로운 String 호환)
    user_id = post.user_id
    if isinstance(user_id, int):
        # 기존 Integer user_id를 String으로 변환
        user_id = str(user_id)
    
    # PostResponse 형태로 반환
    return {
        "id": post.id,
        "user_id": user_id,
        "image_url": post.image_url,
        "title": post.title,
        "description": post.description,
        "recruitment_field": post.recruitment_field,
        "recruitment_headcount": post.recruitment_headcount,
        "school_specific": post.school_specific,
        "target_school_name": post.target_school_name,
        "deadline": post.deadline,
        "external_link": post.external_link,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "application_count": application_count or 0,
        "recruited_count": recruited_count or 0,
        "recruitment_status": recruitment_status
    }

