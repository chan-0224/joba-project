"""
지원서 관련 API 엔드포인트

이 모듈은 공고 지원, 지원서 조회, 지원자 관리 기능을 제공합니다.
모든 엔드포인트는 JWT 토큰 기반 인증이 필요합니다.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Form, Query
from sqlalchemy.orm import Session
from database import get_db, Application, Post, PostQuestion, ApplicationAnswer, User, ApplicationStatusLog
from schemas import (
    ApplicationCreate, ApplicationResponse, ApplicationAnswerCreate,
    ApplicationListItem, ApplicationListResponse, ApplicationDetailResponse,
    ApplicationStatusUpdate, ApplicationStatusResponse, ApplicationSortEnum, ApplicationStatusEnum
)
from services.file_upload_service import FileUploadService
from routers.auth import get_current_user
from services.user_service import get_user_id_from_user
import logging
from datetime import datetime
from typing import Optional, List
import json
from config import settings

router = APIRouter()


@router.post("/applications", response_model=ApplicationResponse, status_code=201)
async def create_application(
    application_data: str = Form(..., description="지원서 데이터(JSON 문자열) - key: application_data"),
    portfolio_files: Optional[List[UploadFile]] = File(None, description="첨부파일 타입 질문에 대한 파일들"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    공고 지원 - 커스터마이징된 질문에 대한 답변 제출
    
    **JWT 인증 필요** - 로그인한 사용자만 지원 가능
    
    Args:
        application_data: 지원서 데이터 (공고 ID, 답변 목록)
        portfolio_files: 첨부파일 목록 (ATTACHMENT 타입 질문용, 선택사항)
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션
        
    Returns:
        ApplicationResponse: 생성된 지원서 정보 (ID, 상태, 생성시간 등)
        
    Raises:
        HTTPException: 
            - 404: 공고를 찾을 수 없음
            - 400: 중복 지원, 필수 질문 미답변, 파일 크기 초과, 질문 미설정
            - 500: 지원서 저장 실패
    
    Note:
        - 같은 공고에 중복 지원 불가
        - 모든 필수 질문에 답변 필요
        - ATTACHMENT 타입 질문은 파일 업로드 필수
        - 파일 크기 제한: 1GB (settings.MAX_FILE_SIZE_BYTES)
    """
    try:
        # 0. application_data(JSON 문자열) 파싱
        try:
            parsed = json.loads(application_data)
            application_obj = ApplicationCreate(**parsed)
        except Exception:
            raise HTTPException(status_code=400, detail="application_data 형식이 올바르지 않습니다.")

        # 1. 공고 존재 여부 확인
        post = db.query(Post).filter(Post.id == application_obj.post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="공고를 찾을 수 없습니다."
            )
        
        # 2. 중복 지원 확인 (같은 사용자가 같은 공고에 중복 지원 방지)
        existing_application = db.query(Application).filter(
            Application.user_id == get_user_id_from_user(current_user),
            Application.post_id == application_obj.post_id
        ).first()
        
        if existing_application:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="이미 지원한 공고입니다."
            )
        
        # 3. 공고의 커스텀 질문들 조회
        post_questions = db.query(PostQuestion).filter(
            PostQuestion.post_id == application_obj.post_id
        ).all()
        
        if not post_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이 공고에는 질문이 설정되지 않았습니다."
            )
        
        # 4. 필수 질문 답변 검증 (모든 필수 질문에 답변이 있는지 확인)
        required_questions = [q for q in post_questions if q.is_required]
        answered_question_ids = [answer.post_question_id for answer in application_obj.answers]
        
        missing_required_questions = []
        for question in required_questions:
            if question.id not in answered_question_ids:
                missing_required_questions.append(question.question_content)
        
        if missing_required_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"다음 필수 질문에 답변해주세요: {', '.join(missing_required_questions)}"
            )
        
        # 5. 답변의 질문 ID 유효성 검증 (실제 존재하는 질문인지 확인)
        valid_question_ids = [q.id for q in post_questions]
        invalid_answers = []
        for answer in application_obj.answers:
            if answer.post_question_id not in valid_question_ids:
                invalid_answers.append(answer.post_question_id)
        
        if invalid_answers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 질문 ID가 포함되어 있습니다: {invalid_answers}"
            )
        
        # 6. 파일 업로드 처리 (ATTACHMENT 타입 질문용)
        file_upload_results = {}
        if portfolio_files:
            for file in portfolio_files or []:
                # 파일 크기 검증 (1GB 제한)
                if file.size and file.size > settings.MAX_FILE_SIZE_BYTES:
                    raise HTTPException(
                        status_code=400,
                        detail=f"파일 크기는 {settings.MAX_FILE_SIZE_BYTES // (1024*1024*1024)}GB를 초과할 수 없습니다: {file.filename}"
                    )
                
                # GCS에 파일 업로드
                file_url = await FileUploadService.upload_portfolio(file)
                file_upload_results[file.filename] = file_url
        
        # 7. 지원서 생성
        application = Application(
            post_id=application_obj.post_id,
            user_id=get_user_id_from_user(current_user),
            status="제출됨"
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        # 8. 답변들 저장 (질문 타입에 따라 처리)
        for answer_data in application_obj.answers:
            # ATTACHMENT 타입 질문의 경우 파일 URL로 대체
            question = db.query(PostQuestion).filter(PostQuestion.id == answer_data.post_question_id).first()
            
            if question.question_type == "ATTACHMENT":
                # 파일명을 기반으로 업로드된 파일 URL 찾기
                file_url = None
                for filename, url in file_upload_results.items():
                    if filename in answer_data.answer_content:
                        file_url = url
                        break
                
                if not file_url:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"ATTACHMENT 타입 질문에 대한 파일을 찾을 수 없습니다: {answer_data.answer_content}"
                    )
                
                answer_content = file_url
            else:
                answer_content = answer_data.answer_content
            
            # 답변 저장
            answer = ApplicationAnswer(
                application_id=application.id,
                post_question_id=answer_data.post_question_id,
                answer_content=answer_content
            )
            db.add(answer)
        
        db.commit()
        
        return ApplicationResponse(
            id=application.id,
            post_id=application.post_id,
            user_id=application.user_id,
            status=application.status,
            created_at=application.created_at,
            updated_at=application.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"지원서 저장 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="지원서 저장에 실패했습니다."
        )


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    지원서 상세 조회 (본인의 지원서만 조회 가능)
    
    **JWT 인증 필요** - 지원자 본인만 자신의 지원서 조회 가능
    
    Args:
        application_id: 조회할 지원서 ID
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션
        
    Returns:
        ApplicationResponse: 지원서 기본 정보 (ID, 상태, 생성/수정 시간)
        
    Raises:
        HTTPException: 
            - 404: 지원서를 찾을 수 없음 (또는 권한 없음)
    
    Note:
        - 본인의 지원서만 조회 가능 (user_id 기반 필터링)
        - 질문과 답변은 포함되지 않음 (기본 정보만)
    """
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == get_user_id_from_user(current_user)  # 본인의 지원서만 조회 가능
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="지원서를 찾을 수 없습니다."
        )
    
    return application


# ==================== 지원자 관리 API ====================

@router.get("/posts/{post_id}/applications", response_model=ApplicationListResponse)
async def get_post_applications(
    post_id: int,
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    status: Optional[str] = Query(None, description="상태 필터"),
    sort_by: ApplicationSortEnum = Query(ApplicationSortEnum.CREATED_AT_DESC, description="정렬 기준"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 공고에 대한 지원자 목록 조회 (모집자만 접근 가능)
    
    **JWT 인증 필요** - 공고 작성자만 해당 공고의 지원자 목록 조회 가능
    
    Args:
        post_id: 공고 ID
        page: 페이지 번호 (기본값: 1, 최소: 1)
        size: 페이지 크기 (기본값: 20, 범위: 1~100)
        status: 상태 필터 ("제출됨", "합격", "불합격", "취소됨", 선택사항)
        sort_by: 정렬 기준 (CREATED_AT_DESC, CREATED_AT_ASC, STATUS)
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션
        
    Returns:
        ApplicationListResponse: 지원자 목록, 총 개수, 페이지네이션 정보
        - User.nickname과 JOIN하여 지원자 닉네임 포함
        
    Raises:
        HTTPException: 
            - 404: 공고를 찾을 수 없음
            - 403: 권한 없음 (공고 작성자가 아님)
    
    Note:
        - 공고 작성자만 접근 가능 (post.user_id == get_user_id_from_user(current_user) 검증)
        - User 테이블과 JOIN하여 지원자 닉네임 포함
    """
    # 1. 공고 존재 여부 및 권한 확인
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공고를 찾을 수 없습니다."
        )
    
    # 2. 권한 검증 - 공고 작성자만 접근 가능
    if post.user_id != get_user_id_from_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 공고의 지원자 목록을 조회할 권한이 없습니다."
        )
    
    # 3. 지원자 목록 조회 (사용자 닉네임과 함께)
    query = db.query(Application, User.name).join(
        User, Application.user_id == User.user_id
    ).filter(Application.post_id == post_id)
    
    # 상태 필터 적용
    if status:
        query = query.filter(Application.status == status)
    
    # 정렬 적용
    if sort_by == ApplicationSortEnum.CREATED_AT_DESC:
        query = query.order_by(Application.created_at.desc())
    elif sort_by == ApplicationSortEnum.CREATED_AT_ASC:
        query = query.order_by(Application.created_at.asc())
    elif sort_by == ApplicationSortEnum.STATUS:
        query = query.order_by(Application.status.asc(), Application.created_at.desc())
    
    # 전체 개수 조회
    total_count = query.count()
    
    # 페이지네이션 적용
    offset = (page - 1) * size
    applications = query.offset(offset).limit(size).all()
    
    # 응답 데이터 구성
    application_items = []
    for application, nickname in applications:
        application_items.append(ApplicationListItem(
            application_id=application.id,
            user_id=application.user_id,
            applicant_name=nickname or "알 수 없음",
            status=application.status,
            submitted_at=application.created_at
        ))
    
    return ApplicationListResponse(
        total_count=total_count,
        applications=application_items,
        page=page,
        size=size
    )


@router.get("/applications/{application_id}/detail", response_model=ApplicationDetailResponse)
async def get_application_detail(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    지원서 상세 조회 (모집자 또는 지원자 본인만 접근 가능)
    
    **JWT 인증 필요** - 지원자 본인 또는 공고 작성자만 접근 가능
    
    Args:
        application_id: 조회할 지원서 ID
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션
        
    Returns:
        ApplicationDetailResponse: 지원서 상세 정보
        - 지원자 정보 (user_id, 닉네임)
        - 지원서 상태 및 제출 시간
        - 모든 질문과 답변 (LEFT JOIN으로 미답변 질문도 포함)
        
    Raises:
        HTTPException: 
            - 404: 지원서 또는 연결된 공고를 찾을 수 없음
            - 403: 권한 없음 (지원자 본인도 공고 작성자도 아님)
    
    Note:
        - 모집자가 조회 시 감사 로그만 기록 (상태 변경 없음)
        - PostQuestion과 ApplicationAnswer LEFT JOIN으로 모든 질문 포함
        - User 테이블과 JOIN하여 지원자 닉네임 포함
    """
    # 1. 지원서 존재 여부 확인
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="지원서를 찾을 수 없습니다."
        )
    
    # 2. 권한 검증
    post = db.query(Post).filter(Post.id == application.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="연결된 공고를 찾을 수 없습니다."
        )
    
    # 지원자 본인이거나 공고 작성자인 경우만 접근 가능
    from services.user_service import get_user_id_from_user
    current_user_id = get_user_id_from_user(current_user)
    if application.user_id != current_user_id and post.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 지원서를 조회할 권한이 없습니다."
        )
    
    # 3. 지원자 정보 조회
    applicant = db.query(User).filter(User.user_id == application.user_id).first()
    
    # 4. 질문과 답변 조회 (LEFT JOIN으로 모든 질문과 해당 답변)
    questions_answers = db.query(
        PostQuestion, ApplicationAnswer
    ).outerjoin(
        ApplicationAnswer, 
        (PostQuestion.id == ApplicationAnswer.post_question_id) & 
        (ApplicationAnswer.application_id == application_id)
    ).filter(
        PostQuestion.post_id == application.post_id
    ).all()
    
    # 5. 응답 데이터 구성
    questions = []
    for question, answer in questions_answers:
        question_data = {
            "question_id": question.id,
            "question_type": question.question_type,
            "question_content": question.question_content,
            "answer_content": answer.answer_content if answer else None
        }
        questions.append(question_data)
    
    # 6. 모집자가 조회한 경우 감사 로그만 기록 (상태 변경 없음)
    if post.user_id == current_user_id:
        # 감사 로그 기록
        status_log = ApplicationStatusLog(
            application_id=application.id,
            previous_status=application.status,
            new_status=application.status,
            changed_by_user_id=current_user.id,
            change_reason="상세 조회"
        )
        db.add(status_log)
        db.commit()
    
    return ApplicationDetailResponse(
        application_id=application.id,
        user_id=application.user_id,
        applicant_name=applicant.name or "알 수 없음",
        status=application.status,
        submitted_at=application.created_at,
        questions=questions
    )


@router.patch("/applications/{application_id}/status", response_model=ApplicationStatusResponse)
async def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    지원서 상태 변경 (합격/불합격 결정)
    
    **JWT 인증 필요** - 공고 작성자만 지원서 상태 변경 가능
    
    Args:
        application_id: 상태를 변경할 지원서 ID
        status_update: 새로운 상태 정보 (ApplicationStatusUpdate)
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션
        
    Returns:
        ApplicationStatusResponse: 업데이트된 지원서 상태 정보
        - application_id, status, updated_at 포함
        
    Raises:
        HTTPException: 
            - 404: 지원서 또는 연결된 공고를 찾을 수 없음
            - 403: 권한 없음 (공고 작성자가 아님)
            - 400: 이미 최종 결정됨 ("합격" 또는 "불합격" 상태)
    
    Note:
        - "합격", "불합격" 상태에서는 재변경 불가
        - 모든 상태 변경은 ApplicationStatusLog에 기록됨
        - updated_at 자동 갱신 (datetime.utcnow())
    """
    # 1. 지원서 존재 여부 확인
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="지원서를 찾을 수 없습니다."
        )
    
    # 2. 권한 검증
    post = db.query(Post).filter(Post.id == application.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="연결된 공고를 찾을 수 없습니다."
        )
    
    if post.user_id != get_user_id_from_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 지원서의 상태를 변경할 권한이 없습니다."
        )
    
    # 3. 상태 변경 제한 확인 (이미 최종 결정된 경우)
    if application.status in ["합격", "불합격"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 최종 결정이 완료된 지원서입니다."
        )
    
    # 4. 상태 변경
    previous_status = application.status
    application.status = status_update.new_status
    application.updated_at = datetime.utcnow()
    
    # 5. 감사 로그 기록
    status_log = ApplicationStatusLog(
        application_id=application.id,
        previous_status=previous_status,
        new_status=status_update.new_status,
        changed_by_user_id=current_user.id
    )
    db.add(status_log)
    db.commit()
    
    return ApplicationStatusResponse(
        application_id=application.id,
        status=application.status,
        updated_at=application.updated_at
    )


@router.patch("/applications/{application_id}/cancel", response_model=ApplicationStatusResponse)
async def cancel_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    지원서 취소 (지원자 본인만 가능)
    
    **JWT 인증 필요** - 지원자 본인만 자신의 지원서 취소 가능
    
    Args:
        application_id: 취소할 지원서 ID
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션
        
    Returns:
        ApplicationStatusResponse: 취소된 지원서 상태 정보
        - application_id, status("취소됨"), updated_at 포함
        
    Raises:
        HTTPException: 
            - 404: 지원서를 찾을 수 없음
            - 403: 권한 없음 (지원자 본인이 아님)
            - 400: 취소 불가능한 상태 ("제출됨" 상태가 아님)
    
    Note:
        - "제출됨" 상태에서만 취소 가능
        - 이미 처리된 지원서("합격", "불합격")는 취소 불가
        - 취소 시 ApplicationStatusLog에 "지원자 취소" 사유로 기록
        - updated_at 자동 갱신 (datetime.utcnow())
    """
    # 1. 지원서 존재 여부 확인
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="지원서를 찾을 수 없습니다."
        )
    
    # 2. 권한 검증 - 지원자 본인만 취소 가능
    if application.user_id != get_user_id_from_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 지원서만 취소할 수 있습니다."
        )
    
    # 3. 취소 가능 상태 확인
    if application.status != "제출됨":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 처리된 지원서는 취소할 수 없습니다."
        )
    
    # 4. 지원서 취소
    previous_status = application.status
    application.status = "취소됨"
    application.updated_at = datetime.utcnow()
    
    # 5. 감사 로그 기록
    status_log = ApplicationStatusLog(
        application_id=application.id,
        previous_status=previous_status,
        new_status="취소됨",
        changed_by_user_id=current_user.id,
        change_reason="지원자 취소"
    )
    db.add(status_log)
    db.commit()
    
    return ApplicationStatusResponse(
        application_id=application.id,
        status=application.status,
        updated_at=application.updated_at
    )


 