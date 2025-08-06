import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_URL: str
    
    # GCP 설정
    GCP_PROJECT_ID: str
    GCS_BUCKET_NAME: str
    GCP_SERVICE_ACCOUNT_KEY_JSON: str
    
    # 서버 설정
    UV_PORT: int = 8000
    
    # JWT 설정
    JWT_SECRET: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7일
    JWT_SIGNUP_TOKEN_EXPIRE_MINUTES: int = 15  # 15분
    
    # 파일 업로드 설정
    MAX_FILE_SIZE_BYTES: int = 1024 * 1024 * 1024  # 1GB
    
    # 소셜 로그인 설정 - Kakao
    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET: str
    KAKAO_REDIRECT_URI: str
    
    # 소셜 로그인 설정 - Naver
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str
    NAVER_REDIRECT_URI: str
    NAVER_STATE: str = None  # 환경변수에서 가져오거나 랜덤 생성
    
    # 소셜 로그인 설정 - Google
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_required_settings()
    
    def _validate_required_settings(self):
        """필수 환경변수 검증"""
        missing_vars = []
        
        # 데이터베이스 검증
        if not self.DATABASE_URL:
            missing_vars.append("DATABASE_URL")
        
        # GCP 검증
        if not self.GCP_PROJECT_ID:
            missing_vars.append("GCP_PROJECT_ID")
        if not self.GCS_BUCKET_NAME:
            missing_vars.append("GCS_BUCKET_NAME")
        if not self.GCP_SERVICE_ACCOUNT_KEY_JSON:
            missing_vars.append("GCP_SERVICE_ACCOUNT_KEY_JSON")
        
        # JWT 검증
        if not self.JWT_SECRET:
            missing_vars.append("JWT_SECRET")
        
        # 소셜 로그인 검증
        if not self.KAKAO_CLIENT_ID:
            missing_vars.append("KAKAO_CLIENT_ID")
        if not self.KAKAO_CLIENT_SECRET:
            missing_vars.append("KAKAO_CLIENT_SECRET")
        if not self.KAKAO_REDIRECT_URI:
            missing_vars.append("KAKAO_REDIRECT_URI")
        
        if not self.NAVER_CLIENT_ID:
            missing_vars.append("NAVER_CLIENT_ID")
        if not self.NAVER_CLIENT_SECRET:
            missing_vars.append("NAVER_CLIENT_SECRET")
        if not self.NAVER_REDIRECT_URI:
            missing_vars.append("NAVER_REDIRECT_URI")
        
        if not self.GOOGLE_CLIENT_ID:
            missing_vars.append("GOOGLE_CLIENT_ID")
        if not self.GOOGLE_CLIENT_SECRET:
            missing_vars.append("GOOGLE_CLIENT_SECRET")
        if not self.GOOGLE_REDIRECT_URI:
            missing_vars.append("GOOGLE_REDIRECT_URI")
        
        if missing_vars:
            raise ValueError(f"필수 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")

    model_config = dict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings() 