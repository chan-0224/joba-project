"""
인증 관련 API 엔드포인트

이 모듈은 소셜 로그인(카카오, 네이버, 구글)과 사용자 인증 기능을 제공합니다.
JWT 토큰 기반의 인증 시스템을 사용합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_db, User
from services import kakao_auth, naver_auth, google_auth
from services.user_service import get_or_create_minimal
from security import create_access_token, create_signup_token, decode_token
from pydantic import BaseModel, HttpUrl, field_validator
from urllib.parse import urlencode
import os

router = APIRouter(prefix="/auth")


def get_current_user(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    """
    JWT 토큰을 검증하여 현재 사용자 정보를 반환
    
    Args:
        authorization: Authorization 헤더 (Bearer 토큰)
        db: 데이터베이스 세션
        
    Returns:
        User: 현재 인증된 사용자 객체
        
    Raises:
        HTTPException: 토큰 없음, 토큰 만료, 사용자 없음
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")
    
    token = authorization.split()[1]
    payload = decode_token(token)  # exp/만료 검증
    
    if not payload:
        raise HTTPException(401, "Invalid or expired token")
    
    user = db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(404, "User not found")
    
    return user


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    """
    현재 로그인된 사용자 정보 조회
    
    Args:
        current_user: 현재 인증된 사용자
        
    Returns:
        dict: 사용자 정보 (ID, 이메일, 닉네임, 트랙, 온보딩 상태)
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "track": current_user.track,
        "is_onboarded": current_user.is_onboarded,
    }


def extract_email_and_id(provider: str, raw: dict):
    """
    소셜 로그인 제공자별로 이메일과 사용자 ID를 추출
    
    Args:
        provider: 소셜 로그인 제공자 ("kakao", "naver", "google")
        raw: 소셜 로그인 API에서 받은 원본 데이터
        
    Returns:
        tuple: (email, provider_user_id)
        
    Raises:
        HTTPException: 알 수 없는 제공자
    """
    if provider == "kakao":
        return (raw.get("kakao_account", {}).get("email"), str(raw.get("id")))
    if provider == "naver":
        data = raw.get("response") if isinstance(raw, dict) and "response" in raw else raw or {}
        email = data.get("email")
        pid = data.get("id")
        return (email, pid)
    if provider == "google":
        return (raw.get("email"), str(raw.get("sub") or raw.get("id")))
    raise HTTPException(400, "unknown provider")


# ==================== 소셜 로그인 API ====================

@router.get("/login/kakao")
async def login_kakao(frontRedirect: str = Query(None, description="프론트엔드 리다이렉트 URL")):
    """
    카카오 로그인 시작
    
    Args:
        frontRedirect: 로그인 완료 후 리다이렉트할 프론트엔드 URL
    
    Returns:
        RedirectResponse: 카카오 로그인 페이지로 리다이렉트
    """
    return RedirectResponse(kakao_auth.get_login_url(frontRedirect))


@router.get("/kakao/callback")
async def kakao_callback(
    code: str = Query(..., description="카카오에서 받은 인증 코드"),
    state: str = Query(None, description="프론트엔드 리다이렉트 URL"),
    db: Session = Depends(get_db)
):
    """
    카카오 로그인 콜백 처리
    
    Args:
        code: 카카오에서 받은 인증 코드
        state: 프론트엔드 리다이렉트 URL (frontRedirect)
        db: 데이터베이스 세션
        
    Returns:
        RedirectResponse: 프론트엔드로 302 리다이렉트
    """
    # 기본 프론트엔드 URL 설정
    front_redirect = state or os.getenv("FRONT_DEFAULT_REDIRECT", "http://localhost:5173/oauth/callback/kakao")
    
    try:
        token = kakao_auth.get_access_token(code)
        raw = kakao_auth.get_user_info(token)
        email, pid = extract_email_and_id("kakao", raw)
        
        if not pid:
            raise HTTPException(400, "카카오 사용자의 id를 가져올 수 없습니다.")

        user, _ = get_or_create_minimal(db, provider="kakao", provider_user_id=pid, email=email)

        if not user.is_onboarded:
            # 신규 회원: 회원가입 필요
            signup_token = create_signup_token({"uid": user.id})
            params = {
                "requires_signup": "true",
                "signup_token": signup_token,
                "email": user.email or ""
            }
            redirect_url = f"{front_redirect}?{urlencode(params)}"
            return RedirectResponse(redirect_url, status_code=302)
        
        # 기존 회원: 로그인 완료
        access_token = create_access_token({"sub": str(user.id)})
        params = {"token": access_token}
        redirect_url = f"{front_redirect}?{urlencode(params)}"
        return RedirectResponse(redirect_url, status_code=302)
        
    except Exception as e:
        # 에러 발생 시 프론트엔드로 에러 정보와 함께 리다이렉트
        params = {"error": str(e)}
        redirect_url = f"{front_redirect}?{urlencode(params)}"
        return RedirectResponse(redirect_url, status_code=302)


@router.get("/login/naver")
async def login_naver():
    """
    네이버 로그인 시작
    
    Returns:
        RedirectResponse: 네이버 로그인 페이지로 리다이렉트
    """
    return RedirectResponse(naver_auth.get_login_url())


@router.get("/naver/callback")
async def naver_callback(code: str, state: str, db: Session = Depends(get_db)):
    """
    네이버 로그인 콜백 처리
    
    Args:
        code: 네이버에서 받은 인증 코드
        state: CSRF 방지를 위한 state 값
        db: 데이터베이스 세션
        
    Returns:
        JSONResponse: 회원가입 필요 여부와 토큰 정보
    """
    token = naver_auth.get_access_token(code, state)
    raw = naver_auth.get_user_info(token)
    email, pid = extract_email_and_id("naver", raw)
    
    if not pid:
        raise HTTPException(400, "네이버 사용자의 id를 가져올 수 없습니다.")

    user, _ = get_or_create_minimal(db, provider="naver", provider_user_id=pid, email=email)

    if not user.is_onboarded:
        signup_token = create_signup_token({"uid": user.id})
        return JSONResponse({"requires_signup": True, "signup_token": signup_token, "email": user.email})
    
    access = create_access_token({"sub": str(user.id)})
    return JSONResponse({"requires_signup": False, "access_token": access, "user_id": user.id})


@router.get("/login/google")
async def login_google():
    """
    구글 로그인 시작
    
    Returns:
        RedirectResponse: 구글 로그인 페이지로 리다이렉트
    """
    return RedirectResponse(google_auth.get_login_url())


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    구글 로그인 콜백 처리
    
    Args:
        code: 구글에서 받은 인증 코드
        db: 데이터베이스 세션
        
    Returns:
        JSONResponse: 회원가입 필요 여부와 토큰 정보
    """
    token = google_auth.get_access_token(code)
    raw = google_auth.get_user_info(token)
    email, pid = extract_email_and_id("google", raw)
    
    if not pid:
        raise HTTPException(400, "구글 사용자의 id를 가져올 수 없습니다.")

    user, _ = get_or_create_minimal(db, provider="google", provider_user_id=pid, email=email)

    if not user.is_onboarded:
        signup_token = create_signup_token({"uid": user.id})
        return JSONResponse({"requires_signup": True, "signup_token": signup_token, "email": user.email})
    
    access = create_access_token({"sub": str(user.id)})
    return JSONResponse({"requires_signup": False, "access_token": access, "user_id": user.id})


# ==================== 회원가입 API ====================

class SignupForm(BaseModel):
    """회원가입 완료를 위한 폼 데이터"""
    signup_token: str
    nickname: str
    track: str        # "frontend"|"backend"|"plan"|"design"|"data"
    school: str
    portfolio_url: HttpUrl | None = None

    @field_validator("track")
    @classmethod
    def check_track(cls, v):
        """트랙 값 검증"""
        allowed = {"frontend", "backend", "plan", "design", "data"}
        if v not in allowed:
            raise ValueError(f"track must be one of {allowed}")
        return v


@router.post("/signup")
async def complete_signup(form: SignupForm, db: Session = Depends(get_db)):
    """
    회원가입 완료 (온보딩 정보 입력)
    
    Args:
        form: 회원가입 폼 데이터
        db: 데이터베이스 세션
        
    Returns:
        dict: 액세스 토큰과 사용자 ID
        
    Raises:
        HTTPException: 유효하지 않은 토큰, 사용자 없음
    """
    try:
        payload = decode_token(form.signup_token)
        if payload.get("typ") != "signup":
            raise ValueError("not signup token")
        user_id = int(payload["uid"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired signup token")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if user.is_onboarded:
        # 이미 완료된 경우 바로 access 토큰 발급
        access = create_access_token({"sub": str(user.id)})
        return {"access_token": access, "user_id": user.id}

    # 온보딩 정보 업데이트
    user.nickname = form.nickname
    user.track = form.track
    user.school = form.school
    user.portfolio_url = str(form.portfolio_url) if form.portfolio_url else None
    user.is_onboarded = True

    db.commit()
    db.refresh(user)

    access = create_access_token({"sub": str(user.id)})
    return {"access_token": access, "user_id": user.id} 