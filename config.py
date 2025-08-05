import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    GCP_PROJECT_ID: str
    GCS_BUCKET_NAME: str
    GCP_SERVICE_ACCOUNT_KEY_JSON: str
    UV_PORT: int = 8000

    # 소셜 로그인 설정
    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET: str
    KAKAO_REDIRECT_URI: str

    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str
    NAVER_REDIRECT_URI: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    JWT_SECRET: str

    model_config = dict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings() 