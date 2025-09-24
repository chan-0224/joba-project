import os
import httpx
import secrets

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")
NAVER_STATE = os.getenv("NAVER_STATE", secrets.token_urlsafe(32))

def get_login_url(front_redirect: str = None):
    """
    네이버 로그인 URL 생성
    
    Args:
        front_redirect: 로그인 완료 후 리다이렉트할 프론트엔드 URL (선택사항)
        
    Returns:
        str: 네이버 OAuth 로그인 URL
    
    Note:
        - front_redirect가 있으면 state에 포함, 없으면 기본 NAVER_STATE 사용
        - 환경변수: NAVER_CLIENT_ID, NAVER_REDIRECT_URI 사용
    """
    # frontRedirect가 있으면 state에 포함, 없으면 기본값 사용
    state = front_redirect if front_redirect else NAVER_STATE
    return (
        f"https://nid.naver.com/oauth2.0/authorize"
        f"?response_type=code"
        f"&client_id={NAVER_CLIENT_ID}"
        f"&redirect_uri={NAVER_REDIRECT_URI}"
        f"&state={state}"
    )

def get_access_token(code: str, state: str):
    """
    네이버에서 액세스 토큰 받기
    
    Args:
        code: 네이버에서 받은 인증 코드
        state: 상태값 (front_redirect 또는 기본 NAVER_STATE)
        
    Returns:
        str: 네이버 액세스 토큰
    
    Note:
        - 환경변수: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 사용
        - 응답의 access_token 필드 반환
    """
    token_url = "https://nid.naver.com/oauth2.0/token"
    params = {
        "grant_type": "authorization_code",
        "client_id": NAVER_CLIENT_ID,
        "client_secret": NAVER_CLIENT_SECRET,
        "code": code,
        "state": state,
    }

    response = httpx.post(token_url, params=params)
    return response.json().get("access_token")

def get_user_info(token: str):
    """
    네이버 사용자 정보 조회
    
    Args:
        token: 네이버 액세스 토큰
        
    Returns:
        dict: 네이버 사용자 정보 (response 필드 내용)
        - id: 네이버 사용자 고유 ID
        - email: 이메일 주소
    
    Note:
        - 네이버 API의 응답 구조: {"response": {실제 사용자 정보}}
        - response 필드만 반환하여 직접 사용 가능
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get("https://openapi.naver.com/v1/nid/me", headers=headers)
    return response.json().get("response")  # 실제 사용자 정보는 'response' 키에 들어있음 