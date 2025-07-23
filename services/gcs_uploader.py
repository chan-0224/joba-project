import json
from google.cloud import storage
from google.oauth2 import service_account
from fastapi import UploadFile
from config import settings
import uuid
import os
import logging

# GCP 인증 정보 파싱
try:
    service_account_info = json.loads(settings.GCP_SERVICE_ACCOUNT_KEY_JSON)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
except Exception as e:
    logging.error("GCP 서비스 계정 키 로딩 실패: %s", e)
    credentials = None

project_id = settings.GCP_PROJECT_ID
bucket_name = settings.GCS_BUCKET_NAME

def upload_file_to_gcs(file_object: UploadFile, destination_blob_name: str) -> str:
    if credentials is None:
        raise Exception("GCP 인증 정보가 올바르지 않습니다.")
    try:
        client = storage.Client(credentials=credentials, project=project_id)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        # 파일을 읽어서 업로드
        blob.upload_from_file(file_object.file, content_type=file_object.content_type)
        # blob.make_public()  # Uniform bucket-level access 환경에서는 사용 불가, 삭제
        return f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
    except Exception as e:
        logging.error("GCS 파일 업로드 실패: %s", e)
        raise

def generate_unique_blob_name(original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1]
    return f"posts/images/{uuid.uuid4().hex}{ext}" 