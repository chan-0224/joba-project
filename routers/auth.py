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
from pydantic import BaseModel, HttpUrl, field_validator, AliasChoices, EmailStr, Field
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
    
    # payload["sub"]가 user_id (문자열)이므로 User 테이블에서 직접 조회
    user_id = payload["sub"]
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(404, "User not found")
    
    return user


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    """
    현재 로그인된 사용자 정보 조회
    
    **JWT 인증 필요** - Bearer 토큰으로 사용자 인증 후 정보 반환
    
    Args:
        current_user: 현재 인증된 사용자 (get_current_user dependency)
        
    Returns:
        dict: 사용자 정보
        - id: DB 내부 ID (integer)
        - user_id: 소셜 로그인 기반 문자열 ID (예: "kakao_12345")
        - email: 이메일 주소
        - nickname: 닉네임
        - track: 트랙 정보
        - is_onboarded: 온보딩 완료 여부
    
    Note:
        - user_id는 소셜 로그인 제공자에 따라 동적 생성
        - 토큰 검증 실패 시 401 에러 반환
    """
    # user_id 생성
    user_id = None
    if current_user.kakao_id:
        user_id = f"kakao_{current_user.kakao_id}"
    elif current_user.naver_id:
        user_id = f"naver_{current_user.naver_id}"
    elif current_user.google_id:
        user_id = f"google_{current_user.google_id}"
    
    return {
        "id": current_user.id,
        "user_id": user_id,
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
    
    **인증 불필요** - 카카오 OAuth 로그인 페이지로 리다이렉트
    
    Args:
        frontRedirect: 로그인 완료 후 리다이렉트할 프론트엔드 URL (선택사항)
    
    Returns:
        RedirectResponse: 카카오 로그인 페이지로 302 리다이렉트
    
    Note:
        - frontRedirect는 URL 디코딩 처리됨
        - 카카오 OAuth state 파라미터로 frontRedirect 전달
        - 로그 기록을 위한 logging 포함
    """
    # URL 디코딩 처리
    from urllib.parse import unquote
    decoded_redirect = unquote(frontRedirect) if frontRedirect else None
    
    # 디버깅을 위한 로그 추가
    import logging
    logging.info(f"카카오 로그인 시작 - frontRedirect: {frontRedirect}, decoded: {decoded_redirect}")
    
    login_url = kakao_auth.get_login_url(decoded_redirect)
    logging.info(f"생성된 카카오 로그인 URL: {login_url}")
    
    return RedirectResponse(login_url)


@router.get("/kakao/callback")
async def kakao_callback(
    code: str = Query(..., description="카카오에서 받은 인증 코드"),
    state: str = Query(None, description="프론트엔드 리다이렉트 URL"),
    db: Session = Depends(get_db)
):
    """
    카카오 로그인 콜백 처리
    
    **인증 불필요** - 카카오 OAuth 콜백을 처리하고 프론트엔드로 리다이렉트
    
    Args:
        code: 카카오에서 받은 인증 코드 (필수)
        state: 프론트엔드 리다이렉트 URL (frontRedirect, 선택사항)
        db: 데이터베이스 세션
        
    Returns:
        RedirectResponse: 프론트엔드로 302 리다이렉트
        - 신규 회원: requires_signup=true, signup_token 포함
        - 기존 회원: token(JWT) 포함
        - 에러 시: error 메시지 포함
    
    Note:
        - state 파라미터 URL 디코딩 처리
        - HTTPS 강제 리다이렉트 (프로덕션 환경, localhost 제외)
        - 사용자 생성/조회는 get_or_create_minimal 함수 사용
        - 모든 에러는 프론트엔드로 리다이렉트하여 처리
    """
    # URL 디코딩 처리
    from urllib.parse import unquote
    front_redirect = unquote(state) if state else os.getenv("FRONT_DEFAULT_REDIRECT", "http://localhost:5173/oauth/callback/kakao")
    
    # 디버깅을 위한 로그 추가
    import logging
    logging.info(f"카카오 콜백 - code: {code[:10]}..., state: {state}, front_redirect: {front_redirect}")
    
    # 프로덕션 환경에서 HTTPS 강제 리다이렉트 확인 (로컬 제외)
    if front_redirect.startswith("http://") and "localhost" not in front_redirect:
        front_redirect = front_redirect.replace("http://", "https://")
        logging.info(f"HTTPS로 변경된 front_redirect: {front_redirect}")
    
    try:
        token = kakao_auth.get_access_token(code)
        raw = kakao_auth.get_user_info(token)
        email, pid = extract_email_and_id("kakao", raw)
        
        if not pid:
            raise HTTPException(400, "카카오 사용자의 id를 가져올 수 없습니다.")

        user, user_id, _ = get_or_create_minimal(db, provider="kakao", provider_user_id=pid, email=email)

        if not user.is_onboarded:
            # 신규 회원: 회원가입 필요
            signup_token = create_signup_token({"uid": user_id})
            params = {
                "requires_signup": "true",
                "signup_token": signup_token,
                "email": user.email or ""
            }
            redirect_url = f"{front_redirect}?{urlencode(params)}"
            logging.info(f"신규 회원 리다이렉트 URL: {redirect_url}")
            return RedirectResponse(redirect_url, status_code=302)
        
        # 기존 회원: 로그인 완료
        access_token = create_access_token({"sub": user_id})
        params = {"token": access_token}
        redirect_url = f"{front_redirect}?{urlencode(params)}"
        logging.info(f"기존 회원 리다이렉트 URL: {redirect_url}")
        return RedirectResponse(redirect_url, status_code=302)
        
    except Exception as e:
        # 에러 발생 시 프론트엔드로 에러 정보와 함께 리다이렉트
        import traceback
        error_msg = str(e)
        logging.error(f"카카오 콜백 에러: {error_msg}\n{traceback.format_exc()}")
        params = {"error": error_msg}
        redirect_url = f"{front_redirect}?{urlencode(params)}"
        logging.info(f"에러 리다이렉트 URL: {redirect_url}")
        return RedirectResponse(redirect_url, status_code=302)


@router.get("/login/naver")
async def login_naver(frontRedirect: str = Query(None, description="프론트엔드 리다이렉트 URL")):
    """
    네이버 로그인 시작
    
    Args:
        frontRedirect: 로그인 완료 후 리다이렉트할 프론트엔드 URL
    
    Returns:
        RedirectResponse: 네이버 로그인 페이지로 리다이렉트
    """
    return RedirectResponse(naver_auth.get_login_url(frontRedirect))


@router.get("/naver/callback")
async def naver_callback(
    code: str = Query(..., description="네이버에서 받은 인증 코드"),
    state: str = Query(None, description="프론트엔드 리다이렉트 URL"),
    db: Session = Depends(get_db)
):
    """
    네이버 로그인 콜백 처리
    
    Args:
        code: 네이버에서 받은 인증 코드
        state: 프론트엔드 리다이렉트 URL (frontRedirect)
        db: 데이터베이스 세션
        
    Returns:
        RedirectResponse: 프론트엔드로 302 리다이렉트
    """
    # 기본 프론트엔드 URL 설정
    front_redirect = state or os.getenv("FRONT_DEFAULT_REDIRECT", "http://localhost:5173/oauth/callback/naver")
    
    try:
        token = naver_auth.get_access_token(code, state)
        raw = naver_auth.get_user_info(token)
        email, pid = extract_email_and_id("naver", raw)
        
        if not pid:
            raise HTTPException(400, "네이버 사용자의 id를 가져올 수 없습니다.")

        user, user_id, _ = get_or_create_minimal(db, provider="naver", provider_user_id=pid, email=email)

        if not user.is_onboarded:
            # 신규 회원: 회원가입 필요
            signup_token = create_signup_token({"uid": user_id})
            params = {
                "requires_signup": "true",
                "signup_token": signup_token,
                "email": user.email or ""
            }
            redirect_url = f"{front_redirect}?{urlencode(params)}"
            return RedirectResponse(redirect_url, status_code=302)
        
        # 기존 회원: 로그인 완료
        access_token = create_access_token({"sub": user_id})
        params = {"token": access_token}
        redirect_url = f"{front_redirect}?{urlencode(params)}"
        return RedirectResponse(redirect_url, status_code=302)
        
    except Exception as e:
        # 에러 발생 시 프론트엔드로 에러 정보와 함께 리다이렉트
        params = {"error": str(e)}
        redirect_url = f"{front_redirect}?{urlencode(params)}"
        return RedirectResponse(redirect_url, status_code=302)


@router.get("/login/google")
async def login_google(frontRedirect: str = Query(None, description="프론트엔드 리다이렉트 URL")):
    """
    구글 로그인 시작
    
    Args:
        frontRedirect: 로그인 완료 후 리다이렉트할 프론트엔드 URL
    
    Returns:
        RedirectResponse: 구글 로그인 페이지로 리다이렉트
    """
    return RedirectResponse(google_auth.get_login_url(frontRedirect))


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="구글에서 받은 인증 코드"),
    state: str = Query(None, description="프론트엔드 리다이렉트 URL"),
    db: Session = Depends(get_db)
):
    """
    구글 로그인 콜백 처리
    
    Args:
        code: 구글에서 받은 인증 코드
        state: 프론트엔드 리다이렉트 URL (frontRedirect)
        db: 데이터베이스 세션
        
    Returns:
        RedirectResponse: 프론트엔드로 302 리다이렉트
    """
    # 기본 프론트엔드 URL 설정
    front_redirect = state or os.getenv("FRONT_DEFAULT_REDIRECT", "http://localhost:5173/oauth/callback/google")
    
    try:
        token = google_auth.get_access_token(code)
        raw = google_auth.get_user_info(token)
        email, pid = extract_email_and_id("google", raw)
        
        if not pid:
            raise HTTPException(400, "구글 사용자의 id를 가져올 수 없습니다.")

        user, user_id, _ = get_or_create_minimal(db, provider="google", provider_user_id=pid, email=email)

        if not user.is_onboarded:
            # 신규 회원: 회원가입 필요
            signup_token = create_signup_token({"uid": user_id})
            params = {
                "requires_signup": "true",
                "signup_token": signup_token,
                "email": user.email or ""
            }
            redirect_url = f"{front_redirect}?{urlencode(params)}"
            return RedirectResponse(redirect_url, status_code=302)
        
        # 기존 회원: 로그인 완료
        access_token = create_access_token({"sub": user_id})
        params = {"token": access_token}
        redirect_url = f"{front_redirect}?{urlencode(params)}"
        return RedirectResponse(redirect_url, status_code=302)
        
    except Exception as e:
        # 에러 발생 시 프론트엔드로 에러 정보와 함께 리다이렉트
        params = {"error": str(e)}
        redirect_url = f"{front_redirect}?{urlencode(params)}"
        return RedirectResponse(redirect_url, status_code=302)


# ==================== 회원가입 API ====================

class SignupForm(BaseModel):
    """회원가입 완료를 위한 폼 데이터

    프론트 신규 포맷을 그대로 수용합니다.
    허용 키:
    - name → nickname
    - field → track
    - university → school
    - portfolio → portfolio_url
    - email (선택)
    또한 구버전 키(nickname, track, school, portfolio_url)도 그대로 허용합니다.
    """
    signup_token: str
    email: EmailStr | None = None
    nickname: str = Field(validation_alias=AliasChoices("name", "nickname"))
    track: str = Field(validation_alias=AliasChoices("field", "track"))  # "frontend"|"backend"|"plan"|"design"|"data"
    school: str = Field(validation_alias=AliasChoices("university", "school", "univ"))
    portfolio_url: HttpUrl | None = Field(default=None, validation_alias=AliasChoices("portfolio", "portfolio_url"))

    @field_validator("track", mode="before")
    @classmethod
    def normalize_track_korean(cls, v):
        """한글 라벨을 백엔드 내부 영문 값으로 매핑"""
        if v is None:
            return v
        mapping = {
            "프론트엔드": "frontend",
            "백엔드": "backend",
            "기획": "plan",
            "디자인": "design",
            "데이터 분석": "data",
            "데이터": "data",
        }
        s = str(v).strip()
        return mapping.get(s, v)

    @field_validator("track")
    @classmethod
    def check_track(cls, v):
        """트랙 값 검증"""
        allowed = {"frontend", "backend", "plan", "design", "data"}
        if v not in allowed:
            raise ValueError(f"track must be one of {allowed}")
        return v

    @field_validator("portfolio_url", mode="before")
    @classmethod
    def empty_portfolio_to_none(cls, v):
        """빈 문자열 포트폴리오는 None 처리"""
        if v is None:
            return None
        if isinstance(v, str):
            if v.strip() == "":
                return None
            return v.strip()
        return None

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


@router.post("/signup")
async def complete_signup(form: SignupForm, db: Session = Depends(get_db)):
    """
    회원가입 완료 (온보딩 정보 입력)
    
    **인증 불필요** - signup_token으로 신원 확인 후 온보딩 정보 저장
    
    Args:
        form: 회원가입 폼 데이터 (SignupForm)
        - signup_token: 회원가입 토큰 (필수)
        - nickname: 닉네임 (필수)
        - track: 트랙 ("frontend"|"backend"|"plan"|"design"|"data", 필수)
        - school: 학교명 (필수)
        - portfolio_url: 포트폴리오 URL (선택사항)
        db: 데이터베이스 세션
        
    Returns:
        dict: 액세스 토큰과 사용자 ID
        - access_token: JWT 액세스 토큰
        - user_id: 소셜 기반 사용자 ID (예: "kakao_12345")
        
    Raises:
        HTTPException: 
            - 401: 유효하지 않거나 만료된 signup_token
            - 404: 사용자를 찾을 수 없음
    
    Note:
        - 이미 온보딩 완료된 경우 바로 액세스 토큰 발급
        - 온보딩 완료 후 is_onboarded = True 설정
        - 소셜 기반 user_id 시스템 사용
    """
    try:
        payload = decode_token(form.signup_token)
        if payload.get("typ") != "signup":
            raise ValueError("not signup token")
        user_id = payload["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired signup token")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if user.is_onboarded:
        # 이미 완료된 경우 바로 access 토큰 발급
        access = create_access_token({"sub": user.user_id})
        return {"access_token": access, "user_id": user.user_id}

    # 온보딩 정보 업데이트
    import logging
    user.nickname = form.nickname
    user.track = form.track
    user.school = form.school
    user.portfolio_url = str(form.portfolio_url) if form.portfolio_url else None
    # 이메일이 제공된 경우, 비어있다면 갱신
    if form.email and not user.email:
        user.email = str(form.email)
    user.is_onboarded = True

    db.commit()
    db.refresh(user)
    logging.info(f"signup completed: user_id={user.user_id}, nickname={user.nickname}, track={user.track}, school={user.school}, portfolio_url={user.portfolio_url}, email={user.email}")

    access = create_access_token({"sub": user.user_id})
    return {"access_token": access, "user_id": user.user_id} 