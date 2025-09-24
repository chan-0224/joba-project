#!/usr/bin/env python3
"""
데이터베이스 스키마 업데이트 스크립트
Render 서버에서 실행하여 누락된 컬럼을 추가합니다.
"""

import os
import sys
from sqlalchemy import create_engine, text
from database import Base, engine

def update_database_schema():
    """데이터베이스 스키마를 업데이트합니다."""
    try:
        print("데이터베이스 스키마 업데이트 시작...")
        
        # 모든 테이블 생성/업데이트
        Base.metadata.create_all(bind=engine)
        print("✅ Base.metadata.create_all() 완료")
        
        # user_id 컬럼이 없으면 추가
        with engine.connect() as conn:
            # users 테이블에 user_id 컬럼이 있는지 확인
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'user_id'
            """))
            
            if not result.fetchone():
                print("user_id 컬럼이 없습니다. 추가 중...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN user_id VARCHAR(100) UNIQUE
                """))
                conn.commit()
                print("✅ user_id 컬럼 추가 완료")
            else:
                print("✅ user_id 컬럼이 이미 존재합니다")
        
        print("🎉 데이터베이스 스키마 업데이트 완료!")
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_database_schema()
