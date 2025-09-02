# JOBA Backend API 문서

## 📋 목차
1. [인증 API](#인증-api)
2. [공고 관리 API](#공고-관리-api)
3. [커스텀 질문 API](#커스터마이징-질문-api)
4. [지원서 API](#지원서-api)
5. [지원자 관리 API](#지원자-관리-api)
6. [헬스체크 API](#헬스체크-api)
7. [공통 응답 형식](#공통-응답-형식)
8. [에러 코드](#에러-코드)

## 🔐 인증 API

### 소셜 로그인

#### 카카오 로그인
```http
GET /v1/auth/login/kakao
```

#### 네이버 로그인
```http
GET /v1/auth/login/naver
```

#### 구글 로그인
```http
GET /v1/auth/login/google
```

#### 소셜 로그인 콜백
```http
GET /v1/auth/{provider}/callback
```

**응답 예시:**
```json
{
  "requires_signup": true,
  "signup_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "email": "user@example.com"
}
```

#### 회원가입 완료
```http
POST /v1/auth/signup
```

**요청 본문:**
```json
{
  "signup_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "nickname": "홍길동",
  "track": "프론트엔드",
  "school": "서울대학교",
  "portfolio_url": "https://portfolio.com"
}
```

#### 현재 사용자 정보 조회
```http
GET /v1/auth/me
Authorization: Bearer <access_token>
```

## 📝 공고 관리 API

### 공고 생성
```http
POST /v1/posts
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**요청 파라미터:**
- `image`: 이미지 파일 (필수)
- `title`: 공고 제목 (필수)
- `description`: 공고 설명 (필수)
- `recruitment_field`: 모집 분야 (필수)
- `recruitment_headcount`: 모집 인원 (필수)
- `school_specific`: 학교별 모집 여부 (필수)
- `target_school_name`: 대상 학교명 (선택)
- `deadline`: 마감일 (필수)
- `external_link`: 외부 링크 (선택)

**응답 예시:**
```json
{
  "id": 1,
  "user_id": 10,
  "image_url": "https://storage.googleapis.com/bucket/posts/image.jpg",
  "title": "프론트엔드 개발자 모집",
  "description": "React, TypeScript 경험자 모집",
  "recruitment_field": "프론트엔드",
  "recruitment_headcount": "1~2인",
  "school_specific": true,
  "target_school_name": "서울대학교",
  "deadline": "2024-08-31T23:59:59Z",
  "external_link": "https://project-detail.com",
  "created_at": "2024-07-25T10:00:00Z",
  "updated_at": "2024-07-25T10:00:00Z",
  "views": 0
}
```

### 공고 조회
```http
GET /v1/posts/{post_id}
```

### 공고 목록 조회
```http
GET /v1/posts
```

**쿼리 파라미터:**
- `sort`: 정렬 기준 (최신순, 인기순, 랜덤순) - 기본값: 최신순
- `recruitment_field`: 모집 분야 필터
- `recruitment_headcount`: 모집 인원 필터
- `school_name`: 학교명 검색
- `deadline_before`: 모집 마감일 이전 필터
- `q`: 검색 키워드 (제목, 설명에서 검색)
- `page`: 페이지 번호 (기본값: 1)
- `size`: 페이지당 공고 개수 (기본값: 10, 최대: 100)

**정렬 기준 설명:**
- **최신순**: 생성일 내림차순
- **인기순**: 지원자 수 내림차순 → 생성일 내림차순 (동점 시)
- **랜덤순**: 무작위 정렬

**응답 예시:**
```json
{
  "total_count": 25,
  "posts": [
    {
      "id": 1,
      "user_id": 10,
      "image_url": "https://storage.googleapis.com/bucket/posts/image.jpg",
      "title": "프론트엔드 개발자 모집",
      "description": "React, TypeScript 경험자 모집",
      "recruitment_field": "프론트엔드",
      "recruitment_headcount": "1~2인",
      "school_specific": true,
      "target_school_name": "서울대학교",
      "deadline": "2024-08-31T23:59:59Z",
      "external_link": "https://project-detail.com",
      "created_at": "2024-07-25T10:00:00Z",
      "updated_at": "2024-07-25T10:00:00Z",
      "views": 15
    }
  ]
}
```

### 공고 옵션 조회
```http
GET /v1/posts/options
```

**응답 예시:**
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

## ❓ 커스터마이징 질문 API

### 질문 생성
```http
POST /v1/posts/{post_id}/questions
Authorization: Bearer <access_token>
```

**요청 본문:**
```json
{
  "questions": [
    {
      "question_type": "TEXT_BOX",
      "question_content": "지원 동기는 무엇인가요?",
      "is_required": true
    },
    {
      "question_type": "LINK",
      "question_content": "포트폴리오 링크를 남겨주세요.",
      "is_required": false
    },
    {
      "question_type": "CHOICES",
      "question_content": "선호하는 개발 환경은?",
      "is_required": true,
      "choices": ["VS Code", "IntelliJ", "Vim", "기타"]
    }
  ]
}
```

### 질문 조회
```http
GET /v1/posts/{post_id}/questions
```

## 📄 지원서 API

### 지원서 제출
```http
POST /v1/applications
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**요청 파라미터:**
- `application_data`: JSON 형태의 지원서 데이터 (Form 필드)
- `portfolio_files`: 첨부파일 (선택, ATTACHMENT 타입 질문용)

**application_data 예시:**
```json
{
  "post_id": 1,
  "answers": [
    {
      "post_question_id": 1,
      "answer_content": "이 공고에 강한 흥미를 느꼈습니다."
    },
    {
      "post_question_id": 2,
      "answer_content": "https://portfolio.com"
    }
  ]
}
```

### 지원서 조회 (본인)
```http
GET /v1/applications/{application_id}
Authorization: Bearer <access_token>
```

## 👥 지원자 관리 API

### 지원자 목록 조회
```http
GET /v1/posts/{post_id}/applications
Authorization: Bearer <access_token>
```

**쿼리 파라미터:**
- `page`: 페이지 번호 (기본값: 1)
- `size`: 페이지 크기 (기본값: 20, 최대: 100)
- `status`: 상태 필터 (선택)
- `sort_by`: 정렬 기준 (최신순, 오래된순, 상태순)

**응답 예시:**
```json
{
  "total_count": 15,
  "applications": [
    {
      "application_id": 1,
      "applicant_id": 10,
      "applicant_nickname": "홍길동",
      "status": "제출됨",
      "submitted_at": "2024-07-25T10:00:00Z"
    },
    {
      "application_id": 2,
      "applicant_id": 11,
      "applicant_nickname": "김철수",
      "status": "합격",
      "submitted_at": "2024-07-25T11:00:00Z"
    }
  ],
  "page": 1,
  "size": 20
}
```

### 지원서 상세 조회 (모집자용)
```http
GET /v1/applications/{application_id}/detail
Authorization: Bearer <access_token>
```

**응답 예시:**
```json
{
  "application_id": 1,
  "applicant_id": 10,
  "applicant_nickname": "홍길동",
  "status": "열람됨",
  "submitted_at": "2024-07-25T10:00:00Z",
  "questions": [
    {
      "question_id": 1,
      "question_type": "TEXT_BOX",
      "question_content": "지원 동기는 무엇인가요?",
      "answer_content": "이 공고에 강한 흥미를 느꼈습니다."
    },
    {
      "question_id": 2,
      "question_type": "LINK",
      "question_content": "포트폴리오 링크를 남겨주세요.",
      "answer_content": "https://portfolio.com"
    },
    {
      "question_id": 3,
      "question_type": "CHOICES",
      "question_content": "선호하는 개발 환경은?",
      "answer_content": "VS Code"
    }
  ]
}
```

### 지원서 상태 변경
```http
PATCH /v1/applications/{application_id}/status
Authorization: Bearer <access_token>
```

### 지원서 취소
```http
PATCH /v1/applications/{application_id}/cancel
Authorization: Bearer <access_token>
```

**응답 예시:**
```json
{
  "application_id": 1,
  "status": "취소됨",
  "updated_at": "2024-07-25T15:30:00Z"
}
```

**요청 본문:**
```json
{
  "new_status": "합격"
}
```

**응답 예시:**
```json
{
  "application_id": 1,
  "status": "합격",
  "updated_at": "2024-07-25T15:30:00Z"
}
```



## 🏥 헬스체크 API

### 서버 상태 확인
```http
GET /ping
```

**응답 예시:**
```json
{
  "message": "pong"
}
```

### 헬스체크
```http
GET /health
```

**응답 예시:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**참고**: 
- 두 엔드포인트 모두 HEAD 요청도 지원하여 UptimeRobot 등 모니터링 도구에서 사용 가능합니다.
- 모든 시간은 UTC 기준으로 반환됩니다.

## 📊 공통 응답 형식

### 성공 응답
API는 직접 데이터를 반환합니다. 공통 래퍼 없이 요청된 리소스의 데이터를 그대로 반환합니다.

**예시:**
```json
// 공고 목록 조회 응답
{
  "total_count": 25,
  "posts": [...]
}

// 사용자 정보 조회 응답
{
  "id": 123,
  "email": "user@example.com",
  "nickname": "홍길동"
}
```

### 에러 응답
```json
{
  "detail": "에러 메시지"
}
```

## ⚠️ 에러 코드

### HTTP 상태 코드
- `200`: 성공
- `201`: 생성됨
- `400`: 잘못된 요청
- `401`: 인증 실패
- `403`: 권한 없음
- `404`: 리소스 없음
- `500`: 서버 오류

### 일반적인 에러 메시지
- `"공고를 찾을 수 없습니다."`
- `"지원서를 찾을 수 없습니다."`
- `"이미 지원한 공고입니다."`
- `"이 공고에는 질문이 설정되지 않았습니다."`
- `"다음 필수 질문에 답변해주세요: [질문 목록]"`
- `"유효하지 않은 질문 ID가 포함되어 있습니다: [ID 목록]"`
- `"파일 크기는 1GB를 초과할 수 없습니다: [파일명]"`
- `"이미지 파일만 업로드 가능합니다."`
- `"이 공고의 지원자 목록을 조회할 권한이 없습니다."`
- `"이 지원서를 조회할 권한이 없습니다."`
- `"이 지원서의 상태를 변경할 권한이 없습니다."`
- `"이미 최종 결정이 완료된 지원서입니다."`
- `"CHOICES 타입 질문에는 선택지가 필요합니다."`

### 파일 업로드 제한
- 최대 1GB까지 업로드 가능
- 파일 형식 제한 없음
- 이미지 파일 업로드 시 `image/` MIME 타입 검증

### 지원서 상태
- `"제출됨"`: 지원서 제출 완료
- `"합격"`: 최종 합격
- `"불합격"`: 최종 불합격
- `"취소됨"`: 지원자가 취소함

### 정렬 옵션
- `"최신순"`: 최근 제출순
- `"오래된순"`: 오래된 제출순
- `"상태순"`: 상태별 정렬

## 🔒 보안 및 권한

### 권한 검증
- 모든 API는 JWT 토큰 기반 인증 필요
- 지원자 목록 조회: 공고 작성자만 접근 가능
- 지원서 상세 조회: 공고 작성자 또는 지원자 본인만 접근 가능
- 상태 변경: 공고 작성자만 가능

### 감사 로그
- 모든 상태 변경은 `application_status_logs` 테이블에 기록
- 변경 이력 추적 가능

### 상태 변경 제한
- `"합격"` 또는 `"불합격"` 상태는 재변경 불가
- 최종 결정 후 추가 변경 시도 시 에러 반환
- `"취소됨"` 상태는 재변경 불가
- 모든 상태 변경은 `application_status_logs` 테이블에 감사 로그 기록 