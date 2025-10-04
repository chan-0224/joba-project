from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from database import User
from routers.auth import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/mypage")


class BasicProfileUpdate(BaseModel):
    field: Optional[str] = None
    university: Optional[str] = None


@router.delete("/users/me")
async def delete_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    회원 탈퇴
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="사용자를 찾을 수 없습니다.")

    db.delete(user)   # 완전 삭제
    db.commit()
    return {"message": "회원 탈퇴가 완료되었습니다."}


@router.put("/users/me/basic")
async def update_basic_info(
    data: BasicProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    마이페이지 - 트랙(field), 대학(university) 수정
    """
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    # 둘 다 선택적으로 수정 가능
    if data.field is not None:
        user.field = data.field
    if data.university is not None:
        user.university = data.university

    db.commit()
    db.refresh(user)

    return {
        "message": "기본 정보가 수정되었습니다.",
        "user_id": user.user_id,
        "field": user.field,
        "university": user.university
    }
