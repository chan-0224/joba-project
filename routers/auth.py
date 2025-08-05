# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_db, User
from services import kakao_auth, naver_auth, google_auth
from services.user_service import get_or_create_minimal
from security import create_access_token, create_signup_token, decode_token
from pydantic import BaseModel, HttpUrl, field_validator

router = APIRouter(prefix="/auth")

# 현재 사용자 가져오기
def get_current_user(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")
    token = authorization.split()[1]
    payload = decode_token(token)  # exp/만료 검증
    user = db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "track": current_user.track,
        "is_onboarded": current_user.is_onboarded,
    }

# 공통 함수: provider별로 이메일과 ID 추출
def extract_email_and_id(provider: str, raw: dict):
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

# ---- Kakao
@router.get("/login/kakao")
def login_kakao():
    return RedirectResponse(kakao_auth.get_login_url())

@router.get("/kakao/callback")
def kakao_callback(code: str, db: Session = Depends(get_db)):
    token = kakao_auth.get_access_token(code)
    raw = kakao_auth.get_user_info(token)
    email, pid = extract_email_and_id("kakao", raw)
    if not pid:
        raise HTTPException(400, "카카오 사용자의 id를 가져올 수 없습니다.")

    user, _ = get_or_create_minimal(db, provider="kakao", provider_user_id=pid, email=email)

    if not user.is_onboarded:
        signup_token = create_signup_token({"uid": user.id})
        return JSONResponse({"requires_signup": True, "signup_token": signup_token, "email": user.email})
    access = create_access_token({"sub": str(user.id)})
    return JSONResponse({"requires_signup": False, "access_token": access, "user_id": user.id})

# ---- Naver
@router.get("/login/naver")
def login_naver():
    return RedirectResponse(naver_auth.get_login_url())

@router.get("/naver/callback")
def naver_callback(code: str, state: str, db: Session = Depends(get_db)):
    token = naver_auth.get_access_token(code, state)
    raw = naver_auth.get_user_info(token)
    email, pid = extract_email_and_id("naver", raw)
    if not pid:
        raise HTTPException(400, "네이버 사용자의id를 가져올 수 없습니다.")

    user, _ = get_or_create_minimal(db, provider="naver", provider_user_id=pid, email=email)

    if not user.is_onboarded:
        signup_token = create_signup_token({"uid": user.id})
        return JSONResponse({"requires_signup": True, "signup_token": signup_token, "email": user.email})
    access = create_access_token({"sub": str(user.id)})
    return JSONResponse({"requires_signup": False, "access_token": access, "user_id": user.id})

# ---- Google
@router.get("/login/google")
def login_google():
    return RedirectResponse(google_auth.get_login_url())

@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    token = google_auth.get_access_token(code)
    raw = google_auth.get_user_info(token)
    email, pid = extract_email_and_id("google", raw)
    if not pid:
        raise HTTPException(400, "구글 사용자의id를 가져올 수 없습니다.")

    user, _ = get_or_create_minimal(db, provider="google", provider_user_id=pid, email=email)

    if not user.is_onboarded:
        signup_token = create_signup_token({"uid": user.id})
        return JSONResponse({"requires_signup": True, "signup_token": signup_token, "email": user.email})
    access = create_access_token({"sub": str(user.id)})
    return JSONResponse({"requires_signup": False, "access_token": access, "user_id": user.id})

# ---- Signup
class SignupForm(BaseModel):
    signup_token: str
    nickname: str
    track: str        # "frontend"|"backend"|"plan"|"design"|"data"
    school: str
    portfolio_url: HttpUrl | None = None

    @field_validator("track")
    @classmethod
    def check_track(cls, v):
        allowed = {"frontend","backend","plan","design","data"}
        if v not in allowed:
            raise ValueError(f"track must be one of {allowed}")
        return v

@router.post("/signup")
def complete_signup(form: SignupForm, db: Session = Depends(get_db)):
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

    user.nickname = form.nickname
    user.track = form.track
    user.school = form.school
    user.portfolio_url = str(form.portfolio_url) if form.portfolio_url else None
    user.is_onboarded = True

    db.commit(); db.refresh(user)

    access = create_access_token({"sub": str(user.id)})
    return {"access_token": access, "user_id": user.id} 