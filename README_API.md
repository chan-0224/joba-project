# JOBA_BACKEND 1차 구현 명세서

## 1. 시스템 개요

- **프레임워크**: FastAPI (Python)
- **DB**: PostgreSQL (SQLAlchemy ORM)
- **파일 저장**: Google Cloud Storage (GCS)
- **배포 환경**: Render
- **환경 변수**: .env 또는 Render 환경 변수 사용 (민감 정보 하드코딩 금지)

---

## 2. 데이터베이스 스키마

### posts 테이블

| 컬럼명                | 타입           | 제약조건 및 설명                                  |
|----------------------|---------------|--------------------------------------------------|
| id                   | INT           | PRIMARY KEY, AUTO_INCREMENT                      |
| user_id              | INT           | NOT NULL, (임시, 인증 미적용)                    |
| image_url            | VARCHAR(255)  | NOT NULL, GCS 이미지 URL                         |
| title                | VARCHAR(255)  | NOT NULL, 공고 제목                              |
| description          | TEXT          | NOT NULL, 공고 설명                              |
| recruitment_field    | VARCHAR(50)   | NOT NULL, 모집 분야                              |
| recruitment_headcount| VARCHAR(50)   | NOT NULL, 모집 인원                              |
| school_specific      | BOOLEAN       | NOT NULL, 특정 학교 제한 여부                    |
| target_school_name   | VARCHAR(100)  | NULLABLE, school_specific이 True일 때만 사용     |
| deadline             | DATETIME      | NOT NULL, 모집 마감일                            |
| external_link        | VARCHAR(255)  | NULLABLE, 외부 링크                              |
| created_at           | DATETIME      | NOT NULL, DEFAULT CURRENT_TIMESTAMP              |
| updated_at           | DATETIME      | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE    |
| views                | INT           | NOT NULL, DEFAULT 0                              |

---

## 3. 환경 변수

| 변수명                        | 설명                                      |
|-------------------------------|-------------------------------------------|
| DATABASE_URL                  | PostgreSQL 접속 URI (예: Neon)             |
| GCP_PROJECT_ID                | GCP 프로젝트 ID                           |
| GCS_BUCKET_NAME               | GCS 버킷 이름                             |
| GCP_SERVICE_ACCOUNT_KEY_JSON  | GCP 서비스 계정 키 (JSON 전체, 문자열)     |
| UV_PORT                       | Uvicorn 포트 (Render 배포 시 $PORT 사용)   |

### 환경 변수 예시 (.env 또는 Render 환경 변수)

```
# Neon(PostgreSQL) 예시
DATABASE_URL=postgresql+psycopg2://<username>:<password>@<host>/<database>

# GCP
GCP_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-gcs-bucket
GCP_SERVICE_ACCOUNT_KEY_JSON='{"type": ... }'  # JSON 전체 문자열

# Render
UV_PORT=10000  # Render에서는 $PORT 환경변수 자동 주입됨
```

---

## 4. API 명세

### 1) 공고 올리기

- **URL**: `/posts`
- **Method**: `POST`
- **Request Type**: `multipart/form-data`
- **Request Body**:
    - **image_file**: (필수) 대표 이미지 파일 (UploadFile)
    - **post_data**: (필수) 아래 필드 포함 (폼 데이터로 전달)
        - user_id: int
        - title: str (최대 255자)
        - description: str
        - recruitment_field: str (최대 50자)
        - recruitment_headcount: str (최대 50자)
        - school_specific: bool
        - target_school_name: Optional[str] (최대 100자)
        - deadline: datetime (ISO 8601 문자열)
        - external_link: Optional[str] (최대 255자)

#### 예시 요청 (multipart/form-data)
| 필드명             | 타입         | 예시값/설명                |
|--------------------|-------------|----------------------------|
| image_file         | 파일         | example.jpg                |
| user_id            | int         | 1                          |
| title              | str         | "2024년 여름 해커톤"      |
| description        | str         | "함께할 팀원을 구합니다"  |
| recruitment_field  | str         | "프론트엔드"             |
| recruitment_headcount | str      | "3~5인"                  |
| school_specific    | bool        | true                       |
| target_school_name | str         | "서울대학교"              |
| deadline           | datetime    | "2024-07-01T23:59:59"    |
| external_link      | str         | "https://example.com"     |

---

### 2) 응답

- **성공시 (201 Created)**
```
{
  "id": 1,
  "user_id": 1,
  "image_url": "https://storage.googleapis.com/your-bucket/posts/images/uuid.jpg",
  "title": "2024년 여름 해커톤",
  "description": "함께할 팀원을 구합니다",
  "recruitment_field": "프론트엔드",
  "recruitment_headcount": "3~5인",
  "school_specific": true,
  "target_school_name": "서울대학교",
  "deadline": "2024-07-01T23:59:59",
  "external_link": "https://example.com",
  "created_at": "2024-06-01T12:00:00",
  "updated_at": "2024-06-01T12:00:00",
  "views": 0
}
```

- **실패시**
    - 400: 이미지 파일이 아닌 경우 등
    - 500: GCS 업로드 실패, DB 저장 실패 등

---

## 5. 기타

- **회원가입/로그인/인증/인가** 기능 없음 (user_id는 외부에서 임시로 전달)
- **공고 목록/상세/수정/삭제** 등은 미구현
- **보안**: 모든 민감 정보는 환경 변수로만 관리 

---
## **에러 요약**
```
ModuleNotFoundError: No module named 'psycopg2'
```
즉, **psycopg2** 패키지가 설치되어 있지 않아서 PostgreSQL(Neon) DB에 연결할 수 없습니다.

---

## **해결 방법**

### 1. requirements.txt에 psycopg2 추가
requirements.txt 파일에 아래 한 줄을 추가하세요:
```
psycopg2-binary
```
> **psycopg2** 대신 **psycopg2-binary**를 사용하는 것이 배포 환경에서 더 간편합니다.

---

### 2. GitHub에 푸시
- requirements.txt 수정 후, 변경사항을 GitHub에 push 하세요.

---

### 3. Render에서 자동 재배포
- GitHub에 푸시하면 Render가 자동으로 다시 배포를 시작합니다.

---

## **정리**
1. requirements.txt에 psycopg2-binary 추가
2. GitHub에 푸시
3. Render에서 재배포 확인

---

이렇게 하면 DB 연결 관련 에러가 해결되고, 서버가 정상적으로 실행될 것입니다!  
추가로 에러가 발생하면, 새 로그를 복사해서 보여주시면 바로 도와드릴 수 있습니다. 