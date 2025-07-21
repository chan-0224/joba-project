import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# .env 파일 로드 (Render 환경에서는 무시됨)
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    GCP_PROJECT_ID: str
    GCS_BUCKET_NAME: str
    GCP_SERVICE_ACCOUNT_KEY_JSON: str
    UV_PORT: int = 8000

    model_config = dict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings() 