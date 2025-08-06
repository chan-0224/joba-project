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
        client = storage.Client(credentials=credentials, project=project_id)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        # 파일 업로드
        blob.upload_from_file(file_object.file, content_type=file_object.content_type)
        return f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
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