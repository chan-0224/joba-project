import os, httpx
from fastapi import HTTPException

def get_login_url(front_redirect: str = None):
    """
    카카오 로그인 URL 생성
    
    Args:
        front_redirect: 로그인 완료 후 리다이렉트할 프론트엔드 URL (선택사항)
        
    Returns:
        str: 카카오 OAuth 로그인 URL
    
    Note:
        - front_redirect는 state 파라미터로 전달
        - 환경변수: KAKAO_CLIENT_ID, KAKAO_REDIRECT_URI 사용
        - URL 인코딩 처리로 안전한 쿼리 스트링 생성
    """
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
    """
    카카오에서 액세스 토큰 받기
    
    Args:
        code: 카카오에서 받은 인증 코드
        
    Returns:
        str: 카카오 액세스 토큰
        
    Raises:
        HTTPException: 
            - 400: 토큰 요청 실패 또는 응답에 access_token 없음
            - 500: 네트워크 요청 오류
    
    Note:
        - 환경변수: KAKAO_CLIENT_ID, KAKAO_CLIENT_SECRET, KAKAO_REDIRECT_URI 사용
        - 10초 타임아웃 설정
    """
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
    """
    카카오 사용자 정보 조회
    
    Args:
        token: 카카오 액세스 토큰
        
    Returns:
        dict: 카카오 사용자 정보
        - id: 카카오 사용자 고유 ID
        - kakao_account.email: 이메일 (동의한 경우)
        
    Raises:
        HTTPException:
            - 400: 사용자 정보 요청 실패
            - 500: 네트워크 요청 오류
    
    Note:
        - 카카오 API v2 사용 (/v2/user/me)
        - 10초 타임아웃 설정
    """
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = httpx.get("https://kapi.kakao.com/v2/user/me", headers=headers, timeout=10.0)
        if response.status_code != 200:
            raise HTTPException(400, f"카카오 사용자 정보 요청 실패: {response.text}")
        
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(500, f"카카오 사용자 정보 요청 중 오류: {str(e)}") 