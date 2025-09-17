import os
import httpx

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


def get_login_url(front_redirect: str = None):
    """구글 로그인 URL 생성"""
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
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
    return response.json() 