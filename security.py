# security.py
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional

# JWT 시크릿 키 - 환경변수에서 가져오며, 없으면 에러 발생
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET 환경변수가 설정되지 않았습니다.")

ALGORITHM = "HS256"

def create_access_token(data: dict, minutes: int = None) -> str:
    if minutes is None:
        # 환경변수에서 가져오되, 없으면 기본값 사용
        minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7일 기본값
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    to_encode.update({"exp": expire, "typ": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_signup_token(data: dict, minutes: int = None) -> str:
    if minutes is None:
        # 환경변수에서 가져오되, 없으면 기본값 사용
        minutes = int(os.getenv("JWT_SIGNUP_TOKEN_EXPIRE_MINUTES", "15"))  # 15분 기본값
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    to_encode.update({"exp": expire, "typ": "signup"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None 
