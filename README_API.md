# JOBA Backend API 문서

## 📋 개요
JOBA 프로젝트의 백엔드 API 서버입니다.

### 서버 정보
- **URL**: `https://joba-project.onrender.com`
- **API 버전**: `v1`
- **프레임워크**: FastAPI
- **데이터베이스**: PostgreSQL (Neon)
- **클라우드 스토리지**: Google Cloud Storage (GCS)

### 라우터 구조
```
/v1
├── /auth          # 인증 (소셜 로그인, JWT)
├── /posts         # 공고 관리
├── /applications  # 지원서 관리
├── /profile       # 프로필 관리
└── /posts/{id}/questions  # 공고별 질문
```

## ⚠️ 중요: API 경로 구조
**모든 API 엔드포인트는 `/v1`으로 시작합니다.**

### 올바른 URL 예시:
- ✅ `https://joba-project.onrender.com/v1/posts` (공고 목록)
- ✅ `https://joba-project.onrender.com/v1/applications` (지원서 목록)
- ✅ `https://joba-project.onrender.com/v1/profile/{user_id}` (프로필 조회)
- ✅ `https://joba-project.onrender.com/v1/auth/login/kakao` (카카오 로그인)

### 잘못된 URL 예시 (중복 경로):
- ❌ `https://joba-project.onrender.com/v1/posts/posts` (중복)
- ❌ `https://joba-project.onrender.com/v1/applications/applications` (중복)
- ❌ `https://joba-project.onrender.com/v1/auth/auth/login/kakao` (중복)

## 🔐 인증 시스템

### 소셜 로그인
- **카카오**: `/v1/auth/login/kakao?frontRedirect={url}` → `/v1/auth/kakao/callback` (302 리다이렉트)
- **네이버**: `/v1/auth/login/naver` → `/v1/auth/naver/callback`
- **구글**: `/v1/auth/login/google` → `/v1/auth/google/callback`

### JWT 토큰  
- **사용자 정보 조회**: `GET /v1/auth/me` (토큰 검증 포함)

### 회원가입
- **회원가입 완료**: `POST /v1/auth/signup` (온보딩 정보 입력)

### 로그인/사용자 생성 정책(변경 사항)
- 소셜 로그인 콜백(카카오/네이버/구글)에서 이메일 동의를 받지 못해도, 제공자 ID(provider id)와 닉네임만으로 사용자 레코드를 생성합니다.
- 기존 사용자 조회는 이메일이 아니라 제공자별 ID(kakao_id/naver_id/google_id)를 우선 사용합니다.
- 인증 디펜던시(`get_current_user`)는 토큰의 `sub`가 `kakao_*/naver_*/google_*` 형태인데 DB에 사용자가 없을 경우 최소 정보로 자동 생성합니다.

## 📝 주요 기능

### 공고 관리
- **생성**: `POST /v1/posts` (이미지 업로드 포함)
- **목록**: `GET /v1/posts` (필터링, 정렬, 검색, 페이지네이션 지원)
- **상세**: `GET /v1/posts/{id}` (지원자 수, 모집된 인원 수, 모집 상태 포함)
- **수정**: `PUT /v1/posts/{id}` (미구현)
- **삭제**: `DELETE /v1/posts/{id}` (미구현)

### 공고 옵션 (프론트엔드 하드코딩)
⚠️ **중요**: 공고 작성 시 사용할 옵션들은 백엔드 API에서 제공하지 않습니다.
프론트엔드에서 다음 상수들을 사용하세요:

```javascript
const RECRUITMENT_FIELDS = ["프론트엔드", "백엔드", "기획", "디자인", "데이터 분석"];
const RECRUITMENT_HEADCOUNTS = ["1~2인", "3~5인", "6~10인", "인원미정"];
```

### 공고 질문 (커스터마이징)
- **생성**: `POST /v1/posts/{id}/questions` (공고 작성자만, 덮어쓰기 방식)
- **조회**: `GET /v1/posts/{id}/questions`
- **지원 타입**: TEXT, TEXTAREA, CHOICES, ATTACHMENT

### 지원서 관리
- **제출**: `POST /v1/applications` (커스터마이징된 질문 답변 + 파일 업로드)
- **상세 조회**: `GET /v1/applications/{id}` (본인만)
- **상세 조회 (모집자용)**: `GET /v1/applications/{id}/detail`
- **상태 변경**: `PATCH /v1/applications/{id}/status` (모집자만)
- **지원 취소**: `PATCH /v1/applications/{id}/cancel` (지원자만)

### 지원자 관리 (모집자용)
- **공고별 지원자 목록**: `GET /v1/posts/{id}/applications` (페이지네이션, 필터링, 정렬)

### 프로필 관리
- **조회**: `GET /v1/profile/{user_id}`
- **수정**: `PUT /v1/profile/{user_id}` (이미지 업로드 포함)
- **시간표 업로드**: `POST /v1/profile/{user_id}/upload/timetable`

## 🚀 CORS 설정
백엔드는 다음 오리진에서의 요청을 허용합니다:
- `http://localhost:5173` (로컬 개발용)
- `http://localhost:3000` (로컬 개발용)
- `http://localhost:8080` (로컬 개발용)
- `https://ssajava-front.vercel.app` (프론트엔드 배포 URL)

## 🔧 환경변수
필수 환경변수:
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `GCP_PROJECT_ID`: Google Cloud 프로젝트 ID
- `GCS_BUCKET_NAME`: GCS 버킷 이름
- `GCP_SERVICE_ACCOUNT_KEY_JSON`: GCP 서비스 계정 키
- `JWT_SECRET`: JWT 서명용 시크릿 키
- 소셜 로그인 관련 키들 (카카오, 네이버, 구글)

## 📊 데이터 구조

### 공고 응답 데이터
- `application_count`: 지원자 수
- `recruited_count`: 모집된 인원 수 (합격자 수)
- `recruitment_status`: 모집 상태 ("모집중" / "마감")
- `recruitment_headcount`: 모집 인원
- `user_id`: 소셜 ID 기반 사용자 식별자 (예: `kakao_123456789`)

### 저장 규칙(변경 사항)
- `posts.user_id`에는 내부 정수 PK가 아닌 소셜 `user_id` 문자열이 저장됩니다. (예: `kakao_123456789`)

### 지원서 상태
- `제출됨`: 초기 지원 상태
- `열람됨`: 모집자가 상세 조회 (현재 미사용)
- `합격`: 모집자가 합격 처리
- `불합격`: 모집자가 불합격 처리
- `취소됨`: 지원자가 직접 취소

### 질문 타입
- `TEXT`: 단일 라인 텍스트 입력
- `TEXTAREA`: 여러 라인 텍스트 입력
- `CHOICES`: 선택지 중 선택
- `ATTACHMENT`: 파일 첨부

## 📚 API 문서
- **Swagger UI**: `https://joba-project.onrender.com/docs`
- **ReDoc**: `https://joba-project.onrender.com/redoc`

## 🚨 문제 해결

### URL 중복 문제
**문제**: `/v1/posts/posts`, `/v1/applications/applications` 같은 중복 경로
**해결**: `main.py`에서 라우터 등록 시 `prefix` 제거

### CORS 설정
**허용된 Origin**:
- `http://localhost:5173` (로컬 개발용)
- `https://ssajava-front.vercel.app` (프론트엔드 배포 URL)

### 프론트엔드 설정
**올바른 환경변수**:
```bash
VITE_API_BASE_URL=https://joba-project.onrender.com/v1
```

### 정렬 파라미터 사용
공고 목록 조회 시 정렬 파라미터는 한글 값을 사용합니다.

허용값:
- 최신순
- 인기순
- 랜덤순

**잘못된 환경변수** (중복 경로 포함):
```bash
VITE_API_BASE_URL=https://joba-project.onrender.com/v1/posts
``` 

## 🗄️ 데이터베이스 스키마 자동 보정(변경 사항)
서버 시작 시 다음 스키마를 자동 점검/보정합니다.
- `users.email`: NULL 허용으로 전환(선택 입력 허용)
- `posts.image_url`: 길이 255 → 500으로 확장
- `posts.user_id`: 문자열(VARCHAR(100))로 강제
- `posts.deadline`: TIMESTAMP WITHOUT TIME ZONE로 정규화
- `posts.views`: 기본값 0 + NOT NULL 보장

## 🖼️ 업로드 공개 정책 참고
- 이미지 업로드는 업로드 직후 공개(`blob.make_public()`)를 시도하여 `https://storage.googleapis.com/{bucket}/{path}`로 접근 가능합니다. 버킷 정책(PAP/UBLA/IAM/ACL)에 따라 공개 설정이 필요합니다.
- 이미지 외 첨부파일(지원서 ATTACHMENT)은 버킷 정책에 따라 공개가 제한될 수 있습니다. 공개 접근이 필요하면 버킷에 공개 권한을 부여하거나(간편) 서명 URL 방식(보안)을 검토하세요.