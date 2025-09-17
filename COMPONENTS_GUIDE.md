# JOBA Backend Components Guide

## 📋 개요
JOBA 백엔드 프로젝트의 구조와 컴포넌트를 설명하는 가이드입니다.

### 프로젝트 구조
```
JOBA_BACKEND/
├── main.py                 # FastAPI 앱 진입점
├── config.py              # 환경변수 및 설정
├── database.py            # 데이터베이스 연결 및 모델
├── security.py            # JWT 토큰 관리
├── routers/               # API 라우터들
│   ├── auth.py           # 인증 관련 API
│   ├── posts.py          # 공고 관리 API
│   ├── applications.py   # 지원서 관리 API
│   ├── profiles.py       # 프로필 관리 API
│   └── post_questions.py # 공고 질문 API
├── services/              # 비즈니스 로직 서비스
│   ├── gcs_uploader.py   # Google Cloud Storage 업로드
│   ├── kakao_auth.py     # 카카오 로그인
│   ├── naver_auth.py     # 네이버 로그인
│   ├── google_auth.py    # 구글 로그인
│   ├── user_service.py   # 사용자 관리
│   └── profile_service.py # 프로필 관리
└── schemas.py             # Pydantic 모델
```

### API 라우터 구조
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

## 🔧 주요 컴포넌트

### 1. main.py
- **역할**: FastAPI 앱 설정 및 라우터 등록
- **주요 기능**:
  - CORS 미들웨어 설정
  - Rate Limiting 설정
  - API 버전 관리 (`/v1` prefix)
  - 라우터 등록

### 2. config.py
- **역할**: 환경변수 관리
- **주요 설정**:
  - 데이터베이스 연결 정보
  - GCP 프로젝트 설정
  - 소셜 로그인 키
  - JWT 시크릿

### 3. database.py
- **역할**: 데이터베이스 연결 및 모델 정의
- **주요 모델**:
  - `User`: 사용자 정보 (프로필 필드 포함)
  - `Post`: 공고 정보
  - `Application`: 지원서 정보
  - `PostQuestion`: 공고 질문
  - `ProfileCareer`: 사용자 경력 정보

### 4. routers/
- **auth.py**: 소셜 로그인, JWT 토큰 관리
- **posts.py**: 공고 CRUD 작업
- **applications.py**: 지원서 관리
- **profiles.py**: 프로필 관리, 이미지 업로드
- **post_questions.py**: 공고별 커스텀 질문

### 5. services/
- **gcs_uploader.py**: Google Cloud Storage 파일 업로드 (프로필 이미지 포함)
- **kakao_auth.py**: 카카오 OAuth2 인증
- **naver_auth.py**: 네이버 OAuth2 인증
- **google_auth.py**: 구글 OAuth2 인증
- **user_service.py**: 사용자 관련 비즈니스 로직
- **profile_service.py**: 프로필 관리 비즈니스 로직

## 🚀 주요 기능

### 인증 시스템
- **소셜 로그인**: 카카오, 네이버, 구글
- **JWT 토큰**: 사용자 인증 및 권한 관리
- **자동 회원가입**: 소셜 로그인 시 자동 계정 생성

### 공고 관리
- **CRUD 작업**: 생성, 조회, 수정, 삭제
- **이미지 업로드**: GCS를 통한 이미지 저장
- **검색 및 필터링**: 다양한 조건으로 공고 검색

### 지원서 시스템
- **커스텀 질문**: 공고별 맞춤 질문 설정
- **파일 첨부**: 포트폴리오 등 파일 업로드
- **상태 관리**: 지원서 상태 추적 및 변경

### 프로필 시스템
- **프로필 관리**: 사용자 기본 정보 및 이미지 관리
- **경력 관리**: 연도별 경력 정보 CRUD
- **이미지 업로드**: 아바타, 커버, 시간표 이미지 업로드
- **프로젝트 히스토리**: 합격한 프로젝트 자동 조회

## 🔒 보안 기능

### CORS 설정
로컬 개발 환경에서의 요청을 허용:
- `http://localhost:5173`
- `http://localhost:3000`
- `http://localhost:8080`

### Rate Limiting
- **ping**: 100회/분
- **health**: 50회/분
- **기타 API**: 기본 제한

### JWT 토큰
- Bearer 토큰 방식
- 7일 만료 (재로그인 필요)

## 🚨 문제 해결

### URL 중복 문제
**문제**: `/v1/posts/posts`, `/v1/applications/applications` 같은 중복 경로
**해결**: `main.py`에서 라우터 등록 시 `prefix` 제거

### 프론트엔드 설정
**올바른 환경변수**:
```bash
VITE_API_BASE_URL=https://joba-project.onrender.com/v1
```

**잘못된 환경변수** (중복 경로 포함):
```bash
VITE_API_BASE_URL=https://joba-project.onrender.com/v1/posts
```

## 📚 API 문서
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **프론트엔드용 명세서**: `FRONTEND_API_SPEC.md`
- **개발자용 문서**: `README_API.md`
