# services/user_service.py
from sqlalchemy.orm import Session
from database import User

PROVIDER_ID_FIELD = {"kakao":"kakao_id","naver":"naver_id","google":"google_id"}

def generate_user_id(provider: str, provider_user_id: str) -> str:
    """
    소셜 ID 기반으로 user_id 생성
    
    Args:
        provider: 소셜 로그인 제공자 ("kakao", "naver", "google")
        provider_user_id: 제공자별 사용자 ID
        
    Returns:
        str: 생성된 user_id (예: "kakao_12345")
    
    Note:
        - 형식: {provider}_{provider_user_id}
        - 전체 시스템에서 사용자 식별자로 활용
    """
    return f"{provider}_{provider_user_id}"

def get_user_id_from_user(user: User) -> str:
    """
    User 객체에서 user_id 추출
    
    Args:
        user: User 객체
        
    Returns:
        str: 소셜 로그인 기반 user_id (예: "kakao_12345")
        
    Raises:
        ValueError: 소셜 ID가 없는 경우
    
    Note:
        - 카카오, 네이버, 구글 순서로 확인
        - 권한 검증 시 사용자 식별에 활용
    """
    if user.kakao_id:
        return f"kakao_{user.kakao_id}"
    elif user.naver_id:
        return f"naver_{user.naver_id}"
    elif user.google_id:
        return f"google_{user.google_id}"
    raise ValueError("No social ID found")

def get_or_create_minimal(db: Session, *, provider: str, provider_user_id: str, email: str | None, name: str | None = None):
    """
    소셜 로그인 사용자 조회 또는 생성
    
    Args:
        db: 데이터베이스 세션
        provider: 소셜 로그인 제공자 ("kakao", "naver", "google")
        provider_user_id: 제공자별 사용자 ID
        email: 이메일 주소 (선택사항)
        
    Returns:
        tuple: (user, user_id, created)
        - user: User 객체
        - user_id: 생성된 user_id 문자열
        - created: 신규 생성 여부 (bool)
    
    Note:
        - 1단계: provider_id로 기존 사용자 조회
        - 2단계: 이메일로 기존 사용자 조회 후 provider_id 연결
        - 3단계: 신규 사용자 생성 (is_onboarded=False)
        - 기존 사용자의 user_id가 없으면 자동 설정
    """
    pid_field = getattr(User, PROVIDER_ID_FIELD[provider])
    user_id = generate_user_id(provider, provider_user_id)

    # 1) provider id로 조회
    user = db.query(User).filter(pid_field == provider_user_id).first()
    if user:
        # 기존 사용자의 user_id가 없으면 설정
        if not user.user_id:
            user.user_id = user_id
            db.commit(); db.refresh(user)
        return user, user_id, False  # created=False

    # 2) email 중복 (이메일 제공된 경우에만)
    if email:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            setattr(existing, PROVIDER_ID_FIELD[provider], provider_user_id)
            # user_id도 설정
            if not existing.user_id:
                existing.user_id = user_id
            # 닉네임이 제공되면 갱신(비어있을 때만)
            if name and not existing.name:
                existing.name = name
            db.commit(); db.refresh(existing)
            return existing, user_id, False

    # 3) 새로(임시) 생성
    user = User(
        email=email,  # None 허용
        user_id=user_id,  # user_id 설정
        name=name,  # 닉네임 저장(없으면 None)
        **{PROVIDER_ID_FIELD[provider]: provider_user_id}, 
        is_onboarded=False
    )
    db.add(user); db.commit(); db.refresh(user)
    return user, user_id, True  # created=True 