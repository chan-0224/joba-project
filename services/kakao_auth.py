import os, httpx
from fastapi import HTTPException

def get_login_url(front_redirect: str = None):
    """카카오 로그인 URL 생성"""
    from urllib.parse import urlencode
    
    params = {
        "response_type": "code",
        "client_id": os.getenv('KAKAO_CLIENT_ID'),
        "redirect_uri": os.getenv('KAKAO_REDIRECT_URI'),
    }
    
    # frontRedirect가 있으면 state에 포함 (URL 인코딩)
    if front_redirect:
        params["state"] = front_redirect
    
    # URL 인코딩을 사용하여 안전하게 쿼리 스트링 생성
    query_string = urlencode(params)
    return f"https://kauth.kakao.com/oauth/authorize?{query_string}"

def get_access_token(code: str):
    """카카오에서 액세스 토큰 받기"""
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": os.getenv("KAKAO_CLIENT_ID"),
        "client_secret": os.getenv("KAKAO_CLIENT_SECRET"),  # client_secret 추가
        "redirect_uri": os.getenv("KAKAO_REDIRECT_URI"),
        "code": code
    }
    
    try:
        response = httpx.post(url, data=data, timeout=10.0)
        if response.status_code != 200:
            raise HTTPException(400, f"카카오 토큰 요청 실패: {response.text}")
        
        result = response.json()
        if "access_token" not in result:
            raise HTTPException(400, f"카카오 토큰 응답에 access_token이 없음: {result}")
        
        return result["access_token"]
    except httpx.RequestError as e:
        raise HTTPException(500, f"카카오 토큰 요청 중 오류: {str(e)}")

def get_user_info(token: str):
    """카카오 사용자 정보 조회"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = httpx.get("https://kapi.kakao.com/v2/user/me", headers=headers, timeout=10.0)
        if response.status_code != 200:
            raise HTTPException(400, f"카카오 사용자 정보 요청 실패: {response.text}")
        
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(500, f"카카오 사용자 정보 요청 중 오류: {str(e)}") 