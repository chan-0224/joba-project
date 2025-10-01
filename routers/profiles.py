from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import json
import logging
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
    
    **인증 불필요** - 모든 사용자의 프로필을 공개적으로 조회 가능
    
    Args:
        user_id (str): 조회할 사용자 ID (소셜 로그인 기반, 예: "kakao_12345")
        db (Session): 데이터베이스 세션

    Returns:
        UserProfileResponse: 사용자 프로필 응답
        - 기본 정보: user_id, email, field, university, portfolio
        - 이미지 URL: avatar_url, banner_url, timetable_url
        - 경력 정보: careers (연도별로 그룹화된 딕셔너리)
        - 최근 프로젝트: recent_projects (최대 2개, 합격한 프로젝트만)

    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 (404)
    
    Note:
        - careers는 연도별로 그룹화되어 반환 (최신 연도 우선)
        - recent_projects는 get_recent_projects 함수로 조회
        - 공개 프로필로 누구나 조회 가능
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
        "name": user.name,
        "field": user.field,
        "university": user.university,
        "portfolio": user.portfolio,
        "avatar_url": user.avatar_url,
        "banner_url": user.banner_url,
        "timetable_url": user.timetable_url,
        "careers": grouped_careers,
        "recent_projects": recent_projects
    }

@router.put("/{user_id}")
def update_user_profile(
    user_id: str,
    name: str = Form(None),
    field: str = Form(None),
    university: str = Form(None),
    portfolio: str = Form(None),
    careers: str = Form(None),  # JSON 문자열
    avatar: UploadFile = File(None),
    banner: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    사용자 프로필을 수정합니다.
    
    **JWT 인증 필요** - 본인만 자신의 프로필 수정 가능
    
    Args:
        user_id (str): 수정할 사용자 ID (소셜 로그인 기반)
        name (str, optional): 이름 (Form 데이터)
        field (str, optional): 트랙 정보 (Form 데이터)
        university (str, optional): 학교 정보 (Form 데이터)
        portfolio (str, optional): 포트폴리오 URL (Form 데이터)
        careers (str, optional): JSON 문자열 형태의 경력 데이터 (Form 데이터)
        avatar (UploadFile, optional): 아바타 이미지 파일
        banner (UploadFile, optional): 배너 이미지 파일
        db (Session): 데이터베이스 세션
        current_user (User): 현재 로그인된 사용자

    Returns:
        dict: 성공 메시지와 업데이트된 사용자 프로필
        - message: 성공 메시지
        - profile: 업데이트된 프로필 정보

    Raises:
        HTTPException:
            - 403 Forbidden: 다른 사용자의 프로필 수정 시도
            - 404 Not Found: 사용자를 찾을 수 없음
    
    Note:
        - Form 데이터와 파일 업로드를 동시에 처리
        - 이미지 업로드 시 GCS에 저장 후 URL 반환
        - careers는 JSON 문자열로 전달되어 파싱됨
        - update_profile 서비스 함수 사용
    """
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not allowed to update this profile")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    avatar_url, banner_url = None, None
    if avatar:
        avatar_url = upload_avatar(avatar, user_id)
    if banner:
        banner_url = upload_cover(banner, user_id)

    # update_profile 과정에서 careers JSON 파싱 오류 등이 발생하면 400으로 변환
    try:
        update_profile(db, user, name, field, university, portfolio, careers, avatar_url, banner_url)
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        logging.warning(f"프로필 업데이트 유효성 오류: {e}")
        raise HTTPException(status_code=400, detail="Invalid profile payload: careers or fields invalid")
    # 최신 상태로 다시 조회하여 일관된 응답 반환
    refreshed = db.query(User).filter(User.user_id == user_id).first()
    recent_projects = get_recent_projects(db, user_id)
    grouped_careers = defaultdict(list)
    for c in sorted(refreshed.careers, key=lambda x: (-x.year, x.id)):
        grouped_careers[str(c.year)].append({
            "id": c.id,
            "description": c.description
        })
    profile = {
        "user_id": refreshed.user_id,
        "email": refreshed.email,
        "name": refreshed.name,
        "field": refreshed.field,
        "university": refreshed.university,
        "portfolio": refreshed.portfolio,
        "avatar_url": refreshed.avatar_url,
        "banner_url": refreshed.banner_url,
        "timetable_url": refreshed.timetable_url,
        "careers": grouped_careers,
        "recent_projects": recent_projects
    }
    return {"message": "프로필이 성공적으로 업데이트되었습니다.", "profile": profile}

@router.post("/{user_id}/upload/timetable")
def upload_timetable_api(
    user_id: str,
    timetable: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    시간표 이미지를 업로드합니다.
    
    **JWT 인증 필요** - 본인만 자신의 시간표 업로드 가능
    
    Args:
        user_id (str): 사용자 ID (소셜 로그인 기반)
        timetable (UploadFile): 업로드된 시간표 이미지 (필수)
        db (Session): 데이터베이스 세션
        current_user (User): 현재 로그인된 사용자

    Returns:
        dict: 업로드된 시간표 이미지 URL
        - timetable_url: GCS에 저장된 시간표 이미지 URL

    Raises:
        HTTPException:
            - 403 Forbidden: 다른 사용자의 프로필 업로드 시도
            - 404 Not Found: 사용자를 찾을 수 없음
    
    Note:
        - GCS의 upload_timetable 함수 사용
        - 업로드 완료 후 User.timetable_url 자동 업데이트
        - 권한 검증: user_id == current_user.user_id
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
