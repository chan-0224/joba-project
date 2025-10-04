from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db, Notice
from schemas import NoticeListItem, NoticeDetailResponse

router = APIRouter(prefix="/notices")

# 1. 공지사항 목록 조회
@router.get("/", response_model=List[NoticeListItem])
async def get_notices(db: Session = Depends(get_db)):
    """
    공지사항 목록 조회 (제목만 표시)
    """
    notices = db.query(Notice).order_by(Notice.created_at.desc()).all()
    return notices


# 2. 공지사항 상세 조회
@router.get("/{notice_id}", response_model=NoticeDetailResponse)
async def get_notice_detail(notice_id: int, db: Session = Depends(get_db)):
    """
    공지사항 상세 조회 (작성일, 제목, 내용)
    """
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다.")
    
    return {
        "id": notice.id,
        "title": notice.title,
        "content": notice.content,
        "created_at": notice.created_at.strftime("%Y-%m-%d") # "YYYY-MM-DD" 형식
    }