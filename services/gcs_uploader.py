import json
from google.cloud import storage
from google.oauth2 import service_account
from fastapi import UploadFile, HTTPException
from config import settings
import uuid
import os
import logging

# GCP 서비스 계정 키 로딩
try:
    service_account_info = eval(settings.GCP_SERVICE_ACCOUNT_KEY_JSON)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    storage_client = storage.Client(credentials=credentials, project=settings.GCP_PROJECT_ID)
except Exception as e:
    logging.error("GCP 서비스 계정 키 로딩 실패: %s", e)
    raise HTTPException(status_code=500, detail="GCP 설정 오류")

bucket = storage_client.bucket(settings.GCS_BUCKET_NAME)

def validate_file_size(file: UploadFile) -> None:
    """파일 크기 검증"""
    if file.size and file.size > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 너무 큽니다. 최대 {settings.MAX_FILE_SIZE_BYTES // (1024*1024*1024)}GB까지 업로드 가능합니다."
        )

def upload_file_to_gcs(file_object: UploadFile, destination_blob_name: str) -> str:
    if credentials is None:
        raise Exception("GCP 인증 정보가 올바르지 않습니다.")
    try:
        blob = bucket.blob(destination_blob_name)
        
        # 파일 업로드
        blob.upload_from_file(file_object.file, content_type=file_object.content_type)
        return f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{destination_blob_name}"
    except Exception as e:
        logging.error("GCS 파일 업로드 실패: %s", e)
        raise

def generate_unique_blob_name(original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1]
    return f"posts/images/{uuid.uuid4().hex}{ext}"

def generate_portfolio_blob_name(original_filename: str) -> str:
    """포트폴리오 파일용 고유 이름 생성"""
    ext = os.path.splitext(original_filename)[1]
    return f"applications/portfolios/{uuid.uuid4().hex}{ext}"

# ---프로필용(프로필 사진, 배경사진, 시간표)---
def generate_profile_image_blob_name(user_id: str, kind: str, original_filename: str) -> str:
    """
    프로필 이미지의 GCS 저장 경로를 생성합니다.

    Args:
        user_id (str): 사용자 ID
        kind (str): 이미지 종류 (avatars, covers, timetables)
        original_filename (str): 원본 파일명

    Returns:
        str: GCS에 저장될 경로 (예: profiles/{user_id}/{kind}/{uuid}.png)
    """
    ext = os.path.splitext(original_filename)[1] or ".png"
    return f"profiles/{user_id}/{kind}/{uuid.uuid4().hex}{ext}"

def upload_profile_image(file: UploadFile, user_id: str, kind: str) -> str:
    """
    프로필 이미지를 검증 후 GCS에 업로드합니다.
    
    업로드 후 public-read 권한을 부여해 외부 접근 가능한 URL을 반환합니다.

    Args:
        file (UploadFile): 업로드된 파일 객체
        user_id (str): 사용자 ID
        kind (str): 이미지 종류 (avatars, covers, timetables)

    Returns:
        str: 업로드된 이미지의 공개 URL

    Raises:
        HTTPException: 이미지 형식/파일 크기 검증 실패 시
        Exception: GCS 업로드 실패 시
    """
    validate_image(file)
    validate_file_size(file)

    dest = generate_profile_image_blob_name(user_id, kind, file.filename)
    url = upload_file_to_gcs(file, dest)

    try:
        if getattr(settings, "GCS_PUBLIC_READ", True):
            blob = bucket.blob(dest)
            try:
                blob.make_public()
            except Exception:
                pass
    except Exception:
        pass

    return url

def upload_avatar(file: UploadFile, user_id: str) -> str:
    """프로필 이미지를 업로드합니다."""
    return upload_profile_image(file, user_id, "avatars")

def upload_cover(file: UploadFile, user_id: str) -> str:
    """커버 이미지를 업로드합니다."""
    return upload_profile_image(file, user_id, "covers")

def upload_timetable(file: UploadFile, user_id: str) -> str:
    """시간표 이미지를 업로드합니다."""
    return upload_profile_image(file, user_id, "timetables")