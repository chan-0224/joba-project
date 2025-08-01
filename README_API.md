# JOBA_BACKEND 2차 구현 명세서

## 1. 시스템 개요

- **프레임워크**: FastAPI (Python)
- **DB**: PostgreSQL (SQLAlchemy ORM, Neon)
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
| recruitment_field    | VARCHAR(50)   | NOT NULL, 모집 분야 (Enum 값)                    |
| recruitment_headcount| VARCHAR(50)   | NOT NULL, 모집 인원 (Enum 값)                    |
| school_specific      | BOOLEAN       | NOT NULL, 특정 학교 제한 여부                    |
| target_school_name   | VARCHAR(100)  | NULLABLE, school_specific이 True일 때만 사용     |
| deadline             | DATETIME      | NOT NULL, 모집 마감일                            |
| external_link        | VARCHAR(255)  | NULLABLE, 외부 링크                              |
| created_at           | DATETIME      | NOT NULL, DEFAULT CURRENT_TIMESTAMP              |
| updated_at           | DATETIME      | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE    |
| views                | INT           | NOT NULL, DEFAULT 0                              |

---

## 3. Enum 정의

### RecruitmentFieldEnum (모집 분야)
- `FRONTEND = "프론트엔드"`
- `BACKEND = "백엔드"`
- `PLANNING = "기획"`
- `DESIGN = "디자인"`
- `DATA_ANALYSIS = "데이터 분석"`

### RecruitmentHeadcountEnum (모집 인원)
- `ONE_TO_TWO = "1~2인"`
- `THREE_TO_FIVE = "3~5인"`
- `SIX_TO_TEN = "6~10인"`
- `UNSPECIFIED = "인원미정"`

### SortEnum (정렬 기준)
- `LATEST = "최신순"`
- `POPULAR = "인기순"`
- `RANDOM = "랜덤순"`

---

## 4. 환경 변수

| 변수명                        | 설명                                      |
|-------------------------------|-------------------------------------------|
| DATABASE_URL                  | PostgreSQL 접속 URI (Neon)                 |
| GCP_PROJECT_ID                | GCP 프로젝트 ID                           |
| GCS_BUCKET_NAME               | GCS 버킷 이름                             |
| GCP_SERVICE_ACCOUNT_KEY_JSON  | GCP 서비스 계정 키 (JSON 전체, 문자열)     |
| UV_PORT                       | Uvicorn 포트 (Render 배포 시 $PORT 사용)   |

### 환경 변수 예시 (.env 또는 Render 환경 변수)

```
# Neon(PostgreSQL) 예시
DATABASE_URL=postgresql://username:password@host/database

# GCP
GCP_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-gcs-bucket
GCP_SERVICE_ACCOUNT_KEY_JSON='{"type": ... }'  # JSON 전체 문자열

# Render
UV_PORT=10000  # Render에서는 $PORT 환경변수 자동 주입됨
```

---

## 5. API 명세

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
        - recruitment_field: RecruitmentFieldEnum
        - recruitment_headcount: RecruitmentHeadcountEnum
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
| recruitment_field  | enum        | "프론트엔드"             |
| recruitment_headcount | enum      | "3~5인"                  |
| school_specific    | bool        | true                       |
| target_school_name | str         | "서울대학교"              |
| deadline           | datetime    | "2024-07-01T23:59:59"    |
| external_link      | str         | "https://example.com"     |

#### 응답 예시
```json
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

### 2) 공고 목록 조회

- **URL**: `/posts`
- **Method**: `GET`
- **Query Parameters**:
    - sort: SortEnum (기본값: "최신순")
    - recruitment_field: Optional[RecruitmentFieldEnum]
    - recruitment_headcount: Optional[RecruitmentHeadcountEnum]
    - school_name: Optional[str]
    - deadline_before: Optional[datetime]
    - q: Optional[str] (검색 키워드)
    - page: int (기본값: 1, 최소값: 1)
    - size: int (기본값: 10, 최소값: 1, 최대값: 100)

#### 예시 요청
```
GET /posts?sort=인기순&recruitment_field=프론트엔드&page=1&size=10
```

#### 응답 예시
```json
{
  "total_count": 25,
  "posts": [
    {
      "id": 1,
      "user_id": 1,
      "image_url": "https://storage.googleapis.com/...",
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
      "views": 15
    }
  ]
}
```

### 3) 공고 상세 조회

- **URL**: `/posts/{post_id}`
- **Method**: `GET`
- **Path Parameters**:
    - post_id: int

#### 예시 요청
```
GET /posts/1
```

#### 응답 예시
```json
{
  "id": 1,
  "user_id": 1,
  "image_url": "https://storage.googleapis.com/...",
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
  "views": 15
}
```

### 4) 공고 옵션 조회

- **URL**: `/posts/options`
- **Method**: `GET`
- **설명**: 공고 작성 시 선택 가능한 모집 분야 및 모집 인원 목록을 반환

#### 응답 예시
```json
{
  "recruitment_fields": [
    "프론트엔드",
    "백엔드",
    "기획",
    "디자인",
    "데이터 분석"
  ],
  "recruitment_headcounts": [
    "1~2인",
    "3~5인",
    "6~10인",
    "인원미정"
  ]
}
```

---

## 6. 에러 응답

### 공통 에러 응답 형식
```json
{
  "detail": "에러 메시지"
}
```

### 주요 에러 코드
- **400**: 잘못된 요청 (이미지 파일이 아닌 경우, 지원하지 않는 정렬 방식 등)
- **404**: 리소스를 찾을 수 없음 (공고를 찾을 수 없습니다)
- **500**: 서버 내부 오류 (이미지 업로드 실패, DB 저장 실패 등)

---

## 7. 배포 및 설정

### 로컬 개발 환경 설정
1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **환경 변수 설정**
   - `.env` 파일 생성
   - 위의 환경 변수 예시 참고하여 설정

3. **서버 실행**
   ```bash
   uvicorn main:app --reload
   ```

### Render 배포 환경 설정
1. **GitHub 연동**
   - GitHub 저장소와 Render 서비스 연결

2. **환경 변수 설정**
   - Render Dashboard → Environment 탭에서 환경 변수 설정

3. **자동 배포**
   - GitHub에 푸시하면 자동으로 재배포

---

## 8. 주요 변경사항 (1차 → 2차)

### 추가된 기능
- ✅ **공고 상세 조회** (`GET /posts/{post_id}`)
- ✅ **공고 옵션 조회** (`GET /posts/options`)
- ✅ **Enum 기반 검색/필터링** (모집 분야, 모집 인원)
- ✅ **랜덤 정렬** 추가
- ✅ **한글 정렬 옵션** (최신순, 인기순, 랜덤순)

### 개선된 사항
- ✅ **코드 일관성** 개선 (주석, 메시지 통일)
- ✅ **에러 메시지 한글화**
- ✅ **Enum 사용으로 타입 안정성** 향상
- ✅ **API 응답 구조** 표준화

---

## 9. 주의사항

- **인증/인가**: 현재 미구현 (user_id는 임시로 전달)
- **파일 업로드**: multipart/form-data 사용
- **데이터베이스**: Neon PostgreSQL 사용
- **파일 저장**: GCP Cloud Storage 사용
- **보안**: 모든 민감 정보는 환경 변수로 관리 