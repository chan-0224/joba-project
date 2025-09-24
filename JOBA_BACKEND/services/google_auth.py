import os
import httpx

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


def get_login_url(front_redirect: str = None):
    """
    구글 로그인 URL 생성
    
    Args:
        front_redirect: 로그인 완료 후 리다이렉트할 프론트엔드 URL (선택사항)
        
    Returns:
        str: 구글 OAuth 로그인 URL
    
    Note:
        - front_redirect는 state 파라미터로 전달
        - scope: email (이메일 주소만 요청)
        - access_type: offline, prompt: consent (리프레시 토큰용)
        - 환경변수: GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URI 사용
    """
    # frontRedirect를 state 파라미터로 전달
    params = [
        f"client_id={GOOGLE_CLIENT_ID}",
        "response_type=code",
        f"redirect_uri={GOOGLE_REDIRECT_URI}",
        "scope=email",
        "access_type=offline",
        "prompt=consent"
    ]
    
    if front_redirect:
        params.append(f"state={front_redirect}")
    
    return "https://accounts.google.com/o/oauth2/v2/auth?" + "&".join(params)


def get_access_token(code: str):
    """
    구글에서 액세스 토큰 받기
    
    Args:
        code: 구글에서 받은 인증 코드
        
    Returns:
        str: 구글 액세스 토큰
    
    Note:
        - 환경변수: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI 사용
        - Content-Type: application/x-www-form-urlencoded
        - 응답의 access_token 필드 반환
    """
    token_url = "https://oauth2.googleapis.com/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = httpx.post(token_url, data=data, headers=headers)
    return response.json().get("access_token")


def get_user_info(token: str):
    """
    구글 사용자 정보 조회
    
    Args:
        token: 구글 액세스 토큰
        
    Returns:
        dict: 구글 사용자 정보
        - sub 또는 id: 구글 사용자 고유 ID
        - email: 이메일 주소
    
    Note:
        - 구글 API v2 사용 (/oauth2/v2/userinfo)
        - sub 필드가 사용자 ID (일부 응답에서는 id 필드)
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
    return response.json() 