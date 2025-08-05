# JOBA Backend API 명세서

## 개요
JOBA 프로젝트의 백엔드 API 서버입니다. 공고 올리기, 커스터마이징 질문 설정, 공고 지원 기능을 제공합니다.

## 기술 스택
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cloud Storage**: Google Cloud Storage (GCS)
- **Deployment**: Render

## 환경 변수
```
DATABASE_URL=postgresql://username:password@host:port/database
GCP_PROJECT_ID=your-project-id
GCS_BUCKET_NAME=your-bucket-name
GCP_SERVICE_ACCOUNT_KEY_JSON={"type": "service_account", ...}
UV_PORT=8000
```

## API 엔드포인트

### 1. 공고 관리

#### 1.1 공고 생성
```
POST /posts
Content-Type: multipart/form-data

Parameters:
- user_id: int (필수)
- title: str (필수, 최대 255자)
- description: str (필수)
- recruitment_field: str (필수) - "프론트엔드", "백엔드", "기획", "디자인", "데이터 분석"
- recruitment_headcount: str (필수) - "1~2인", "3~5인", "6~10인", "인원미정"
- school_specific: bool (필수)
- target_school_name: str (선택, 최대 100자)
- deadline: datetime (필수)
- external_link: str (선택, 최대 255자)
- image: file (필수) - 공고 이미지

Response:
{
  "id": 1,
  "user_id": 123,
  "image_url": "https://storage.googleapis.com/...",
  "title": "프론트엔드 개발자 모집",
  "description": "React, TypeScript 경험자 모집",
  "recruitment_field": "프론트엔드",
  "recruitment_headcount": "1~2인",
  "school_specific": false,
  "target_school_name": null,
  "deadline": "2024-12-31T23:59:59",
  "external_link": null,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00",
  "views": 0
}
```

#### 1.2 공고 목록 조회
```
GET /posts?page=1&size=10&sort=최신순&field=프론트엔드

Parameters:
- page: int (선택, 기본값: 1)
- size: int (선택, 기본값: 10)
- sort: str (선택) - "최신순", "인기순", "랜덤순"
- field: str (선택) - 특정 분야 필터링

Response:
{
  "total_count": 100,
  "posts": [
    {
      "id": 1,
      "user_id": 123,
      "image_url": "https://storage.googleapis.com/...",
      "title": "프론트엔드 개발자 모집",
      "description": "React, TypeScript 경험자 모집",
      "recruitment_field": "프론트엔드",
      "recruitment_headcount": "1~2인",
      "school_specific": false,
      "target_school_name": null,
      "deadline": "2024-12-31T23:59:59",
      "external_link": null,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:00:00",
      "views": 15
    }
  ]
}
```

#### 1.3 공고 상세 조회
```
GET /posts/{post_id}

Response:
{
  "id": 1,
  "user_id": 123,
  "image_url": "https://storage.googleapis.com/...",
  "title": "프론트엔드 개발자 모집",
  "description": "React, TypeScript 경험자 모집",
  "recruitment_field": "프론트엔드",
  "recruitment_headcount": "1~2인",
  "school_specific": false,
  "target_school_name": null,
  "deadline": "2024-12-31T23:59:59",
  "external_link": null,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00",
  "views": 15
}
```

### 2. 질문 커스터마이징

#### 2.1 공고 질문 설정
```
POST /posts/{post_id}/questions
Content-Type: application/json

Request Body:
{
  "questions": [
    {
      "question_type": "TEXT_BOX",
      "question_content": "가장 기억에 남는 프로젝트는 무엇인가요?",
      "is_required": true
    },
    {
      "question_type": "LINK",
      "question_content": "포트폴리오 링크를 공유해주세요.",
      "is_required": false
    },
    {
      "question_type": "ATTACHMENT",
      "question_content": "이력서를 첨부해주세요.",
      "is_required": true
    },
    {
      "question_type": "CHOICES",
      "question_content": "선호하는 개발 환경은?",
      "is_required": true,
      "choices": ["Windows", "Mac", "Linux"]
    }
  ]
}

Response:
{
  "message": "4개의 질문이 성공적으로 생성되었습니다."
}
```

#### 2.2 공고 질문 조회
```
GET /posts/{post_id}/questions

Response:
[
  {
    "id": 1,
    "post_id": 1,
    "question_type": "TEXT_BOX",
    "question_content": "가장 기억에 남는 프로젝트는 무엇인가요?",
    "is_required": true,
    "choices": null,
    "created_at": "2024-01-01T10:00:00"
  },
  {
    "id": 2,
    "post_id": 1,
    "question_type": "CHOICES",
    "question_content": "선호하는 개발 환경은?",
    "is_required": true,
    "choices": ["Windows", "Mac", "Linux"],
    "created_at": "2024-01-01T10:01:00"
  }
]
```

### 3. 공고 지원

#### 3.1 지원서 제출
```
POST /applications
Content-Type: multipart/form-data

Parameters:
- application_data: JSON (필수)
  {
    "post_id": 1,
    "applicant_id": 456,
    "answers": [
      {
        "post_question_id": 1,
        "answer_content": "쇼핑몰 프로젝트입니다."
      },
      {
        "post_question_id": 2,
        "answer_content": "https://github.com/username/portfolio"
      },
      {
        "post_question_id": 3,
        "answer_content": "resume.pdf"
      },
      {
        "post_question_id": 4,
        "answer_content": "Mac"
      }
    ]
  }
- portfolio_files: file[] (선택) - ATTACHMENT 타입 질문에 대한 파일들

Response:
{
  "id": 1,
  "post_id": 1,
  "applicant_id": 456,
  "status": "제출됨",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

#### 3.2 지원서 조회
```
GET /applications/{application_id}

Response:
{
  "id": 1,
  "post_id": 1,
  "applicant_id": 456,
  "status": "제출됨",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

## 질문 타입

### 1. TEXT_BOX
- 텍스트 입력 필드
- 자유롭게 텍스트 입력 가능

### 2. LINK
- URL 링크 입력
- 외부 포트폴리오, 깃허브 등 링크 공유

### 3. ATTACHMENT
- 파일 업로드
- 최대 1GB까지 업로드 가능
- 파일 형식 제한 없음

### 4. CHOICES
- 선택지 중 하나 선택
- choices 배열에 선택지 목록 포함

## 에러 코드

### 400 Bad Request
- 필수 질문 미답변
- 유효하지 않은 질문 ID
- 파일 크기 초과 (1GB)
- 중복 지원

### 404 Not Found
- 공고를 찾을 수 없음
- 지원서를 찾을 수 없음

### 500 Internal Server Error
- 서버 내부 오류
- 파일 업로드 실패

## 배포

### Render 배포 설정
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 환경 변수 설정
Render 대시보드에서 다음 환경 변수들을 설정해야 합니다:
- `DATABASE_URL`
- `GCP_PROJECT_ID`
- `GCS_BUCKET_NAME`
- `GCP_SERVICE_ACCOUNT_KEY_JSON`

## 개발 가이드

### 로컬 개발 환경 설정
1. 가상환경 생성 및 활성화
2. `pip install -r requirements.txt`
3. 환경 변수 설정 (.env 파일)
4. `uvicorn main:app --reload`

### 데이터베이스 마이그레이션
- 새로운 테이블 생성: `post_questions`, `application_answers`
- 기존 `applications` 테이블 스키마 변경

### 테스트
- 각 API 엔드포인트별 단위 테스트 작성 권장
- 파일 업로드 테스트 시 다양한 파일 형식 및 크기 테스트 