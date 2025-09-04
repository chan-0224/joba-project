# services/user_service.py
from sqlalchemy.orm import Session
from database import User

PROVIDER_ID_FIELD = {"kakao":"kakao_id","naver":"naver_id","google":"google_id"}

def generate_user_id(provider: str, provider_user_id: str) -> str:
    """소셜 ID 기반으로 user_id 생성"""
    return f"{provider}_{provider_user_id}"

def get_or_create_minimal(db: Session, *, provider: str, provider_user_id: str, email: str | None):
    pid_field = getattr(User, PROVIDER_ID_FIELD[provider])
    user_id = generate_user_id(provider, provider_user_id)

    # 1) provider id로 조회
    user = db.query(User).filter(pid_field == provider_user_id).first()
    if user:
        return user, user_id, False  # created=False

    # 2) email 중복
    if email:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            setattr(existing, PROVIDER_ID_FIELD[provider], provider_user_id)
            db.commit(); db.refresh(existing)
            return existing, user_id, False

    # 3) 새로(임시) 생성
    user = User(email=email, **{PROVIDER_ID_FIELD[provider]: provider_user_id}, is_onboarded=False)
    db.add(user); db.commit(); db.refresh(user)
    return user, user_id, True  # created=True 