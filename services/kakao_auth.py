import os, httpx

def get_login_url():
    return (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?response_type=code"
        f"&client_id={os.getenv('KAKAO_CLIENT_ID')}"
        f"&redirect_uri={os.getenv('KAKAO_REDIRECT_URI')}"
    )

def get_access_token(code: str):
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": os.getenv("KAKAO_CLIENT_ID"),
        "redirect_uri": os.getenv("KAKAO_REDIRECT_URI"),
        "code": code
    }
    response = httpx.post(url, data=data)
    return response.json().get("access_token")

def get_user_info(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get("https://kapi.kakao.com/v2/user/me", headers=headers)
    return response.json() 