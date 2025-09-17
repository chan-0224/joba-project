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
    """
    특정 사용자의 프로필을 조회합니다.
    
    - 기본 정보(이메일, 트랙, 학교, 포트폴리오 URL, 프로필/커버/시간표 이미지)
    - 연도별 경력 정보
    - 최근 합격 프로젝트 2개

    Args:
        user_id (str): 조회할 사용자 ID
        db (Session): 데이터베이스 세션

    Returns:
        UserProfileResponse: 사용자 프로필 응답

    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 (404)
    """
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
    """
    사용자 프로필을 수정합니다.
    
    - 본인만 자신의 프로필 수정 가능
    - 텍스트 정보와 이미지(프로필사진, 커버사진) 수정 가능
    - careers(JSON 문자열)로 경력 추가/수정/삭제 가능

    Args:
        user_id (str): 수정할 사용자 ID
        track (str, optional): 트랙 정보
        school (str, optional): 학교 정보
        portfolio_url (str, optional): 포트폴리오 URL
        careers (str, optional): JSON 문자열 형태의 경력 데이터
        avatar (UploadFile, optional): 아바타 이미지 파일
        cover (UploadFile, optional): 커버 이미지 파일
        db (Session): 데이터베이스 세션
        current_user (User): 현재 로그인된 사용자

    Returns:
        dict: 성공 메시지와 업데이트된 사용자 프로필

    Raises:
        HTTPException:
            - 403 Forbidden: 다른 사용자의 프로필 수정 시도
            - 404 Not Found: 사용자를 찾을 수 없음
    """
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
    """
    시간표 이미지를 업로드합니다.
    
    - 본인만 자신의 시간표 업로드 가능
    - 업로드된 시간표 URL이 DB에 저장됩니다.

    Args:
        user_id (str): 사용자 ID
        timetable (UploadFile): 업로드된 시간표 이미지
        db (Session): 데이터베이스 세션
        current_user (User): 현재 로그인된 사용자

    Returns:
        dict: 업로드된 시간표 이미지 URL

    Raises:
        HTTPException:
            - 403 Forbidden: 다른 사용자의 프로필 업로드 시도
            - 404 Not Found: 사용자를 찾을 수 없음
    """
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not allowed to update this profile")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    timetable_url = upload_timetable(timetable, user_id)
    user.timetable_url = timetable_url
    db.commit()

    return {"timetable_url": timetable_url}
