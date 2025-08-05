import os
import httpx

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")

def get_login_url():
    state = "naver_random_state"  # 간단한 CSRF 방지용
    return (
        f"https://nid.naver.com/oauth2.0/authorize"
        f"?response_type=code"
        f"&client_id={NAVER_CLIENT_ID}"
        f"&redirect_uri={NAVER_REDIRECT_URI}"
        f"&state={state}"
    )

def get_access_token(code: str, state: str):
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
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get("https://openapi.naver.com/v1/nid/me", headers=headers)
    return response.json().get("response")  # 실제 사용자 정보는 'response' 키에 들어있음 