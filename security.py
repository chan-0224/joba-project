# security.py
import os
from datetime import datetime, timedelta, timezone
from jose import jwt

SECRET_KEY = os.getenv("JWT_SECRET", "change_me")
ALGO = "HS256"

def _utcnow():
    return datetime.now(timezone.utc)

def create_access_token(data: dict, minutes: int = 60*24*14) -> str:
    payload = data | {"iat": _utcnow(), "exp": _utcnow() + timedelta(minutes=minutes), "typ": "access"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def create_signup_token(data: dict, minutes: int = 15) -> str:
    payload = data | {"iat": _utcnow(), "exp": _utcnow() + timedelta(minutes=minutes), "typ": "signup"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGO]) 