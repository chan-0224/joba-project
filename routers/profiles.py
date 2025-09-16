from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from collections import defaultdict
from database import get_db
from services.profile_service import update_profile, get_recent_projects
from schemas import UserProfileResponse
from database import User
from routers.auth import get_current_user
from services.gcs_uploader import upload_avatar, upload_cover, upload_timetable

router = APIRouter(prefix="/profile")

@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    grouped_careers = defaultdict(list)
    for c in sorted(user.careers, key=lambda x: (-x.year, x.id)):
        grouped_careers[str(c.year)].append({
            "id": c.id,
            "description": c.description
        })

    recent_projects = get_recent_projects(db, user.user_id)

    return {
        "user_id": user.user_id,
        "email": user.email,
        "track": user.track,
        "school": user.school,
        "portfolio_url": user.portfolio_url,
        "avatar_url": user.avatar_url,
        "cover_url": user.cover_url,
        "timetable_url": user.timetable_url,
        "careers": grouped_careers,
        "recent_projects": recent_projects
    }

@router.put("/{user_id}")
def update_user_profile(
    user_id: str,
    track: str = Form(None),
    school: str = Form(None),
    portfolio_url: str = Form(None),
    careers: str = Form(None),  # JSON 문자열
    avatar: UploadFile = File(None),
    cover: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not allowed to update this profile")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    avatar_url, cover_url = None, None
    if avatar:
        avatar_url = upload_avatar(avatar, user_id)
    if cover:
        cover_url = upload_cover(cover, user_id)

    updated_user = update_profile(db, user, track, school, portfolio_url, careers, avatar_url, cover_url)
    return {"message": "프로필이 성공적으로 업데이트되었습니다.", "profile": updated_user}

@router.post("/{user_id}/upload/timetable")
def upload_timetable_api(
    user_id: str,
    timetable: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not allowed to update this profile")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    timetable_url = upload_timetable(timetable, user_id)
    user.timetable_url = timetable_url
    db.commit()

    return {"timetable_url": timetable_url}
