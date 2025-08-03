from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Form
from sqlalchemy.orm import Session
from database import get_db, Application, Post
from schemas import ApplicationCreate, ApplicationResponse
from services.gcs_uploader import upload_file_to_gcs, generate_portfolio_blob_name, validate_pdf_file
import logging
from datetime import datetime
from typing import Optional
import json

router = APIRouter()

@router.post("/applications", response_model=ApplicationResponse, status_code=201)
def create_application(
    application_data: ApplicationCreate = Depends(),
    portfolio_pdf_file: Optional[UploadFile] = File(None, description="지원 포트폴리오 PDF 파일"),
    portfolio_url: Optional[str] = Form(None, description="외부 포트폴리오 링크"),
    db: Session = Depends(get_db)
):
    """
    공고 지원 - 파일 업로드 또는 외부 링크 중 하나 선택 가능
    """
    try:
        # 1. 공고 존재 여부 확인
        post = db.query(Post).filter(Post.id == application_data.post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="공고를 찾을 수 없습니다.")
        
        # 2. 중복 지원 확인
        existing_application = db.query(Application).filter(
            Application.applicant_id == application_data.applicant_id,
            Application.post_id == application_data.post_id
        ).first()
        
        if existing_application:
            raise HTTPException(status_code=400, detail="이미 지원한 공고입니다.")
        
        # 3. 포트폴리오 처리
        final_portfolio_url = None
        
        if portfolio_pdf_file and portfolio_url:
            raise HTTPException(
                status_code=400, 
                detail="포트폴리오는 파일 업로드 또는 외부 링크 중 하나만 선택해주세요."
            )
        
        if not portfolio_pdf_file and not portfolio_url:
            raise HTTPException(
                status_code=400, 
                detail="포트폴리오 파일 또는 외부 링크를 제공해주세요."
            )
        
        if portfolio_pdf_file:
            # PDF 파일 업로드
            validate_pdf_file(portfolio_pdf_file)
            filename = portfolio_pdf_file.filename or "portfolio.pdf"
            blob_name = generate_portfolio_blob_name(filename)
            final_portfolio_url = upload_file_to_gcs(portfolio_pdf_file, blob_name)
        
        elif portfolio_url:
            # 외부 링크 사용
            if not portfolio_url.startswith(('http://', 'https://')):
                raise HTTPException(status_code=400, detail="올바른 URL 형식이 아닙니다.")
            final_portfolio_url = portfolio_url
        
        # 4. DB 저장
        application = Application(
            post_id=application_data.post_id,
            applicant_id=application_data.applicant_id,
            motivation=application_data.motivation,
            most_memorable_project=application_data.most_memorable_project,
            portfolio_pdf_url=final_portfolio_url,
            meeting_available_time=application_data.meeting_available_time,
            aspirations=application_data.aspirations,
            status="제출됨"
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        # 5. 해당 공고의 총 지원자 수 조회
        total_applications = db.query(Application).filter(
            Application.post_id == application_data.post_id
        ).count()
        
        # 6. 응답 생성
        return ApplicationResponse(
            id=application.id,
            post_id=application.post_id,
            applicant_id=application.applicant_id,
            motivation=application.motivation,
            most_memorable_project=application.most_memorable_project,
            portfolio_pdf_url=application.portfolio_pdf_url,
            meeting_available_time=application.meeting_available_time,
            aspirations=application.aspirations,
            created_at=application.created_at,
            status=application.status,
            post_title=post.title,
            total_applications=total_applications
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"지원서 저장 실패: {e}")
        raise HTTPException(status_code=500, detail="지원서 저장에 실패했습니다.") 