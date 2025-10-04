from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from database import User
from routers.auth import get_current_user

router = APIRouter(prefix="/mypage")


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


