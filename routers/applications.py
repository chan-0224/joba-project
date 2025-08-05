from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Form
from sqlalchemy.orm import Session
from database import get_db, Application, Post, PostQuestion, ApplicationAnswer
from schemas import ApplicationCreate, ApplicationResponse, ApplicationAnswerCreate
from services.gcs_uploader import upload_file_to_gcs, generate_portfolio_blob_name
import logging
from datetime import datetime
from typing import Optional, List
import json

router = APIRouter()

@router.post("/applications", response_model=ApplicationResponse, status_code=201)
async def create_application(
    application_data: ApplicationCreate,
    portfolio_files: Optional[List[UploadFile]] = File(None, description="첨부파일 타입 질문에 대한 파일들"),
    db: Session = Depends(get_db)
):
    """
    공고 지원 - 커스터마이징된 질문에 대한 답변 제출
    """
    try:
        # 1. 공고 존재 여부 확인
        post = db.query(Post).filter(Post.id == application_data.post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="공고를 찾을 수 없습니다."
            )
        
        # 2. 중복 지원 확인
        existing_application = db.query(Application).filter(
            Application.applicant_id == application_data.applicant_id,
            Application.post_id == application_data.post_id
        ).first()
        
        if existing_application:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="이미 지원한 공고입니다."
            )
        
        # 3. 공고의 질문들 조회
        post_questions = db.query(PostQuestion).filter(
            PostQuestion.post_id == application_data.post_id
        ).all()
        
        if not post_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이 공고에는 질문이 설정되지 않았습니다."
            )
        
        # 4. 필수 질문 답변 검증
        required_questions = [q for q in post_questions if q.is_required]
        answered_question_ids = [answer.post_question_id for answer in application_data.answers]
        
        missing_required_questions = []
        for question in required_questions:
            if question.id not in answered_question_ids:
                missing_required_questions.append(question.question_content)
        
        if missing_required_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"다음 필수 질문에 답변해주세요: {', '.join(missing_required_questions)}"
            )
        
        # 5. 답변의 질문 ID 유효성 검증
        valid_question_ids = [q.id for q in post_questions]
        invalid_answers = []
        for answer in application_data.answers:
            if answer.post_question_id not in valid_question_ids:
                invalid_answers.append(answer.post_question_id)
        
        if invalid_answers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 질문 ID가 포함되어 있습니다: {invalid_answers}"
            )
        
        # 6. 파일 업로드 처리
        file_upload_results = {}
        if portfolio_files:
            for file in portfolio_files:
                if file.size and file.size > 1024 * 1024 * 1024:  # 1GB 제한
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"파일 크기는 1GB를 초과할 수 없습니다: {file.filename}"
                    )
                
                # 파일을 GCS에 업로드
                blob_name = f"applications/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
                file_url = upload_file_to_gcs(file, blob_name)
                file_upload_results[file.filename] = file_url
        
        # 7. 지원서 생성
        application = Application(
            post_id=application_data.post_id,
            applicant_id=application_data.applicant_id,
            status="제출됨"
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        # 8. 답변들 저장
        for answer_data in application_data.answers:
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
            applicant_id=application.applicant_id,
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
    db: Session = Depends(get_db)
):
    """
    지원서 상세 조회
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="지원서를 찾을 수 없습니다."
        )
    
    return application 