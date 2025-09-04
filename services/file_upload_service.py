"""
파일 업로드 공통 서비스
"""

from fastapi import UploadFile, HTTPException
from services.gcs_uploader import upload_file_to_gcs, generate_unique_blob_name, generate_portfolio_blob_name
import logging

class FileUploadService:
    """파일 업로드 공통 서비스"""
    
    @staticmethod
    async def upload_image(file: UploadFile) -> str:
        """
        이미지 파일 업로드
        
        Args:
            file: 업로드할 이미지 파일
            
        Returns:
            str: 업로드된 이미지 URL
            
        Raises:
            HTTPException: 파일 업로드 실패
        """
        try:
            blob_name = generate_unique_blob_name(file.filename or "uploaded_image")
            return upload_file_to_gcs(file, blob_name)
        except Exception as e:
            logging.error(f"이미지 업로드 실패: {e}")
            raise HTTPException(500, "이미지 업로드에 실패했습니다.")
    
    @staticmethod
    async def upload_portfolio(file: UploadFile) -> str:
        """
        포트폴리오 파일 업로드
        
        Args:
            file: 업로드할 포트폴리오 파일
            
        Returns:
            str: 업로드된 파일 URL
            
        Raises:
            HTTPException: 파일 업로드 실패
        """
        try:
            blob_name = generate_portfolio_blob_name(file.filename or "uploaded_file")
            return upload_file_to_gcs(file, blob_name)
        except Exception as e:
            logging.error(f"포트폴리오 업로드 실패: {e}")
            raise HTTPException(500, "포트폴리오 업로드에 실패했습니다.")
