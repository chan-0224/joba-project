# services/user_service.py
from sqlalchemy.orm import Session
from database import User

PROVIDER_ID_FIELD = {"kakao":"kakao_id","naver":"naver_id","google":"google_id"}

def get_or_create_minimal(db: Session, *, provider: str, provider_user_id: str, email: str | None):
    pid_field = getattr(User, PROVIDER_ID_FIELD[provider])

    # 1) provider id로 조회
    user = db.query(User).filter(pid_field == provider_user_id).first()
    if user:
        return user, False  # created=False

    # 2) email 중복
    if email:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            setattr(existing, PROVIDER_ID_FIELD[provider], provider_user_id)
            db.commit(); db.refresh(existing)
            return existing, False

    # 3) 새로(임시) 생성
    user = User(email=email, **{PROVIDER_ID_FIELD[provider]: provider_user_id}, is_onboarded=False)
    db.add(user); db.commit(); db.refresh(user)
    return user, True  # created=True 