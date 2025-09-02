# JOBA Backend API 명세서 (프론트엔드용)

## 📋 목차
1. [개요](#개요)
2. [인증 시스템](#인증-시스템)
3. [공고 관리](#공고-관리)
4. [커스터마이징 질문](#커스터마이징-질문)
5. [지원서 관리](#지원서-관리)
6. [지원자 관리](#지원자-관리)
7. [공통 사항](#공통-사항)

---

## 📖 개요

### 기본 정보
- **Base URL**: `https://joba-project.onrender.com`
- **API 버전**: `v1`
- **인증 방식**: JWT Bearer Token
- **Content-Type**: `application/json` (파일 업로드 시 `multipart/form-data`)

---

## 🔐 인증 시스템

### 소셜 로그인 플로우

#### 1. 로그인 시작
- **카카오 로그인**: `GET /v1/auth/login/kakao`
- **네이버 로그인**: `GET /v1/auth/login/naver`
- **구글 로그인**: `GET /v1/auth/login/google`

#### 2. 콜백 처리
- **URL**: `GET /v1/auth/{provider}/callback?code={code}`
- **응답 예시**:
  ```json
  {
    "requires_signup": true,
    "signup_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "email": "user@example.com"
  }
  ```
  또는 이미 가입된 사용자:
  ```json
  {
    "requires_signup": false,
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 123
  }
  ```

#### 3. 회원가입 완료 (온보딩)
- **URL**: `POST /v1/auth/signup`
- **요청 바디**:
  ```json
  {
    "signup_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "nickname": "홍길동",
    "track": "프론트엔드",
    "school": "서울대학교",
    "portfolio_url": "https://portfolio.com"
  }
  ```
- **응답**:
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 123
  }
  ```

#### 4. 현재 사용자 정보 조회
- **URL**: `GET /v1/auth/me`
- **헤더**: `Authorization: Bearer {access_token}`
- **응답**:
  ```json
  {
    "id": 123,
    "email": "user@example.com",
    "nickname": "홍길동",
    "track": "프론트엔드",
    "is_onboarded": true
  }
  ```

---

## 📝 공고 관리

### 1. 공고 생성
- **URL**: `POST /v1/posts`
- **Content-Type**: `multipart/form-data`
- **헤더**: `Authorization: Bearer {access_token}`
- **요청 바디**:
  - `image`: 이미지 파일
  - `title`: 공고 제목
  - `description`: 공고 설명
  - `recruitment_field`: 모집 분야
  - `recruitment_headcount`: 모집 인원
  - `school_specific`: 학교 특정 여부 (boolean)
  - `target_school_name`: 대상 학교명
  - `deadline`: 마감일 (ISO 8601, UTC 기준)
  - `external_link`: 외부 링크 (선택사항)

- **응답**:
  ```json
  {
    "id": 1,
    "user_id": 123,
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

### 2. 공고 목록 조회
- **URL**: `GET /v1/posts`
- **쿼리 파라미터**:
  - `sort`: 정렬 기준 ("최신순", "인기순", "랜덤순")
  - `recruitment_field`: 모집 분야 필터
  - `recruitment_headcount`: 모집 인원 필터
  - `school_name`: 학교명 필터
  - `deadline_before`: 마감일 필터
  - `q`: 검색 키워드
  - `page`: 페이지 번호 (기본값: 1)
  - `size`: 페이지 크기 (기본값: 10)

- **응답**:
  ```json
  {
    "total_count": 100,
    "posts": [
      {
        "id": 1,
        "user_id": 123,
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

### 3. 공고 상세 조회
- **URL**: `GET /v1/posts/{post_id}`
- **응답**: 공고 생성과 동일한 형식 (조회수 자동 증가)

### 4. 공고 옵션 조회
- **URL**: `GET /v1/posts/options`
- **응답**:
  ```json
  {
    "recruitment_fields": ["프론트엔드", "백엔드", "기획", "디자인", "데이터 분석"],
    "recruitment_headcounts": ["1~2인", "3~5인", "6~10인", "인원미정"]
  }
  ```

---

## ❓ 커스터마이징 질문

### 1. 질문 생성 (공고 작성자만)
- **URL**: `POST /v1/posts/{post_id}/questions`
- **헤더**: `Authorization: Bearer {access_token}`
- **요청 바디**:
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
- **응답**:
  ```json
  {
    "message": "3개의 질문이 성공적으로 생성되었습니다."
  }
  ```

### 2. 질문 조회
- **URL**: `GET /v1/posts/{post_id}/questions`
- **응답**:
  ```json
  [
    {
      "id": 1,
      "post_id": 1,
      "question_type": "TEXT_BOX",
      "question_content": "지원 동기는 무엇인가요?",
      "is_required": true,
      "choices": null,
      "created_at": "2024-07-25T10:00:00Z"
    },
    {
      "id": 2,
      "post_id": 1,
      "question_type": "LINK",
      "question_content": "포트폴리오 링크를 남겨주세요.",
      "is_required": false,
      "choices": null,
      "created_at": "2024-07-25T10:01:00Z"
    },
    {
      "id": 3,
      "post_id": 1,
      "question_type": "CHOICES",
      "question_content": "선호하는 개발 환경은?",
      "is_required": true,
      "choices": ["VS Code", "IntelliJ", "Vim", "기타"],
      "created_at": "2024-07-25T10:02:00Z"
    }
  ]
  ```

---

## 📄 지원서 관리

### 1. 지원서 제출
- **URL**: `POST /v1/applications`
- **Content-Type**: `multipart/form-data`
- **헤더**: `Authorization: Bearer {access_token}`
- **요청 바디**:
  - `application_data`: JSON 문자열 (Form 필드)
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
        },
        {
          "post_question_id": 3,
          "answer_content": "VS Code"
        }
      ]
    }
    ```
  - `portfolio_files`: 첨부파일들 (ATTACHMENT 타입 질문용)

- **응답**:
  ```json
  {
    "id": 1,
    "post_id": 1,
    "applicant_id": 123,
    "status": "제출됨",
    "created_at": "2024-07-25T10:00:00Z",
    "updated_at": "2024-07-25T10:00:00Z"
  }
  ```

### 2. 지원서 조회 (본인)
- **URL**: `GET /v1/applications/{application_id}`
- **헤더**: `Authorization: Bearer {access_token}`
- **응답**: 지원서 제출과 동일한 형식

---

## 👥 지원자 관리

### 1. 지원자 목록 조회 (모집자만)
- **URL**: `GET /v1/posts/{post_id}/applications`
- **헤더**: `Authorization: Bearer {access_token}`
- **쿼리 파라미터**:
  - `page`: 페이지 번호 (기본값: 1)
  - `size`: 페이지 크기 (기본값: 20)
  - `status`: 상태 필터 ("제출됨", "열람됨", "합격", "불합격")
  - `sort_by`: 정렬 기준 ("최신순", "오래된순", "상태순")

- **응답**:
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

### 2. 지원서 상세 조회 (모집자 또는 지원자 본인)
- **URL**: `GET /v1/applications/{application_id}/detail`
- **헤더**: `Authorization: Bearer {access_token}`
- **응답**:
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

### 3. 지원서 상태 변경 (모집자만)
- **URL**: `PATCH /v1/applications/{application_id}/status`
- **헤더**: `Authorization: Bearer {access_token}`
- **요청 바디**:
  ```json
  {
    "new_status": "합격"
  }
  ```
- **응답**:
  ```json
  {
    "application_id": 1,
    "status": "합격",
    "updated_at": "2024-07-25T15:30:00Z"
  }
  ```

### 4. 지원서 취소 (지원자 본인만)
- **URL**: `PATCH /v1/applications/{application_id}/cancel`
- **헤더**: `Authorization: Bearer {access_token}`
- **응답**:
  ```json
  {
    "application_id": 1,
    "status": "취소됨",
    "updated_at": "2024-07-25T15:30:00Z"
  }
  ```



---

## 🔧 공통 사항

### 응답 형식
API는 직접 데이터를 반환합니다. 공통 래퍼 없이 요청된 리소스의 데이터를 그대로 반환합니다.

### 인증 헤더
모든 인증이 필요한 API에서 사용:
```
Authorization: Bearer {access_token}
```

### 파일 업로드
- **파일 크기 제한**: 1GB
- **지원 파일 형식**: 제한 없음
- **Content-Type**: `multipart/form-data`
- **이미지 파일 검증**: 공고 이미지 업로드 시 `image/` MIME 타입 검증

### 상태 코드
- `200`: 성공
- `201`: 생성됨
- `400`: 잘못된 요청 (필수 필드 누락, 유효성 검증 실패)
- `401`: 인증 실패 (토큰 없음, 토큰 만료)
- `403`: 권한 없음 (공고 작성자가 아닌 경우)
- `404`: 리소스 없음 (공고, 지원서를 찾을 수 없음)
- `500`: 서버 오류

### 주요 에러 메시지
- `"공고를 찾을 수 없습니다."`
- `"지원서를 찾을 수 없습니다."`
- `"이미 지원한 공고입니다."`
- `"이 공고에는 질문이 설정되지 않았습니다."`
- `"다음 필수 질문에 답변해주세요: [질문 목록]"`
- `"파일 크기는 1GB를 초과할 수 없습니다: [파일명]"`
- `"이미지 파일만 업로드 가능합니다."`
- `"권한이 없습니다."`
- `"이미 최종 결정이 완료된 지원서입니다."`

### 지원서 상태
- `"제출됨"`: 지원서 제출 완료
- `"합격"`: 최종 합격
- `"불합격"`: 최종 불합격
- `"취소됨"`: 지원자가 취소함

### 질문 타입
- `"TEXT_BOX"`: 텍스트 입력
- `"LINK"`: URL 링크 입력
- `"ATTACHMENT"`: 파일 업로드
- `"CHOICES"`: 선택지 중 하나 선택

### 트랙 타입
- `"프론트엔드"`: 프론트엔드
- `"백엔드"`: 백엔드
- `"기획"`: 기획
- `"디자인"`: 디자인
- `"데이터 분석"`: 데이터 분석

이 명세서를 참고하여 프론트엔드 개발을 진행하시면 됩니다! 🚀 