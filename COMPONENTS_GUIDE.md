# JOBA Backend 컴포넌트 가이드

## 📋 목차
1. [Enum 클래스들](#enum-클래스들)
2. [BaseModel 클래스들](#basemodel-클래스들)
3. [API 엔드포인트들](#api-엔드포인트들)
4. [데이터베이스 모델들](#데이터베이스-모델들)

---

## 🔢 Enum 클래스들

### 📊 RecruitmentFieldEnum (모집 분야)
**위치**: `schemas.py`  
**기능**: 공고에서 모집하는 분야를 정의하는 열거형

```python
FRONTEND = "프론트엔드"      # 프론트엔드 개발자 모집
BACKEND = "백엔드"          # 백엔드 개발자 모집
PLANNING = "기획"           # 기획자 모집
DESIGN = "디자인"           # 디자이너 모집
DATA_ANALYSIS = "데이터 분석" # 데이터 분석가 모집
```

### 👥 RecruitmentHeadcountEnum (모집 인원)
**위치**: `schemas.py`  
**기능**: 공고에서 모집하는 인원 수를 정의하는 열거형

```python
ONE_TO_TWO = "1~2인"        # 1~2명 모집
THREE_TO_FIVE = "3~5인"     # 3~5명 모집
SIX_TO_TEN = "6~10인"       # 6~10명 모집
UNSPECIFIED = "인원미정"     # 인원 미정
```

### 🔄 SortEnum (정렬 기준)
**위치**: `schemas.py`  
**기능**: 공고 목록을 정렬하는 기준을 정의하는 열거형

```python
LATEST = "최신순"           # 최신 등록순으로 정렬
POPULAR = "인기순"          # 지원자 수 기준으로 정렬 (인기순)
RANDOM = "랜덤순"           # 랜덤으로 정렬
```

### 📋 ApplicationStatusEnum (지원서 상태)
**위치**: `schemas.py`  
**기능**: 지원서의 현재 상태를 정의하는 열거형

```python
SUBMITTED = "제출됨"        # 지원서 제출 완료
REVIEWED = "열람됨"         # 모집자가 지원서를 열람함
ACCEPTED = "합격"           # 최종 합격
REJECTED = "불합격"         # 최종 불합격
```

### 📊 ApplicationSortEnum (지원서 정렬)
**위치**: `schemas.py`  
**기능**: 지원자 목록을 정렬하는 기준을 정의하는 열거형

```python
CREATED_AT_DESC = "최신순"  # 최신 지원순으로 정렬
CREATED_AT_ASC = "오래된순"  # 오래된 지원순으로 정렬
STATUS = "상태순"           # 상태별로 정렬
```

### ❓ QuestionTypeEnum (질문 타입)
**위치**: `schemas.py`  
**기능**: 커스터마이징 질문의 타입을 정의하는 열거형

```python
TEXT_BOX = "TEXT_BOX"       # 텍스트 입력 박스
LINK = "LINK"               # URL 링크 입력
ATTACHMENT = "ATTACHMENT"   # 파일 첨부
CHOICES = "CHOICES"         # 선택지 중 하나 선택
```

---

## 📝 BaseModel 클래스들

### 🏢 공고 관련

#### PostCreate
**위치**: `schemas.py`  
**기능**: 새로운 공고를 생성할 때 사용하는 요청 모델
- `title`: 공고 제목
- `description`: 공고 설명
- `recruitment_field`: 모집 분야
- `recruitment_headcount`: 모집 인원
- `school_specific`: 학교 특정 여부
- `target_school_name`: 대상 학교명
- `deadline`: 마감일
- `external_link`: 외부 링크 (선택사항)

#### PostResponse
**위치**: `schemas.py`  
**기능**: 공고 정보를 응답할 때 사용하는 모델
- `id`: 공고 ID
- `user_id`: 작성자 ID
- `image_url`: 공고 이미지 URL
- `title`: 공고 제목
- `description`: 공고 설명
- `recruitment_field`: 모집 분야
- `recruitment_headcount`: 모집 인원
- `school_specific`: 학교 특정 여부
- `target_school_name`: 대상 학교명
- `deadline`: 마감일
- `external_link`: 외부 링크
- `created_at`: 생성일
- `updated_at`: 수정일
- `views`: 조회수

#### PostListResponse
**위치**: `schemas.py`  
**기능**: 공고 목록을 응답할 때 사용하는 모델
- `total_count`: 전체 공고 수
- `posts`: 공고 목록 (PostResponse 배열)

#### PostOptionsResponse
**위치**: `schemas.py`  
**기능**: 공고 작성 시 사용할 수 있는 옵션들을 응답하는 모델
- `recruitment_fields`: 사용 가능한 모집 분야 목록
- `recruitment_headcounts`: 사용 가능한 모집 인원 목록

### ❓ 질문 관련

#### PostQuestionCreate
**위치**: `schemas.py`  
**기능**: 새로운 커스터마이징 질문을 생성할 때 사용하는 모델
- `question_type`: 질문 타입 (TEXT_BOX, LINK, ATTACHMENT, CHOICES)
- `question_content`: 질문 내용
- `is_required`: 필수 여부
- `choices`: 선택지 목록 (CHOICES 타입일 때만 사용)

#### PostQuestionsRequest
**위치**: `schemas.py`  
**기능**: 여러 개의 질문을 한 번에 생성할 때 사용하는 요청 모델
- `questions`: 질문 목록 (PostQuestionCreate 배열)

#### PostQuestionResponse
**위치**: `schemas.py`  
**기능**: 질문 정보를 응답할 때 사용하는 모델
- `id`: 질문 ID
- `post_id`: 공고 ID
- `question_type`: 질문 타입
- `question_content`: 질문 내용
- `is_required`: 필수 여부
- `choices`: 선택지 목록
- `created_at`: 생성일

### 📄 지원서 관련

#### ApplicationCreate
**위치**: `schemas.py`  
**기능**: 새로운 지원서를 제출할 때 사용하는 요청 모델
- `post_id`: 지원할 공고 ID
- `answers`: 답변 목록 (ApplicationAnswerCreate 배열)

#### ApplicationResponse
**위치**: `schemas.py`  
**기능**: 지원서 기본 정보를 응답할 때 사용하는 모델
- `id`: 지원서 ID
- `post_id`: 공고 ID
- `applicant_id`: 지원자 ID
- `status`: 지원서 상태
- `created_at`: 제출일
- `updated_at`: 수정일

#### ApplicationAnswerCreate
**위치**: `schemas.py`  
**기능**: 질문에 대한 답변을 생성할 때 사용하는 모델
- `post_question_id`: 질문 ID
- `answer_content`: 답변 내용

#### ApplicationAnswerResponse
**위치**: `schemas.py`  
**기능**: 질문 답변 정보를 응답할 때 사용하는 모델
- `id`: 답변 ID
- `application_id`: 지원서 ID
- `post_question_id`: 질문 ID
- `answer_content`: 답변 내용
- `created_at`: 작성일

#### ApplicationListItem
**위치**: `schemas.py`  
**기능**: 지원자 목록에서 각 지원자의 기본 정보를 표시하는 모델
- `application_id`: 지원서 ID
- `applicant_id`: 지원자 ID
- `applicant_nickname`: 지원자 닉네임
- `status`: 지원서 상태
- `submitted_at`: 제출일

#### ApplicationListResponse
**위치**: `schemas.py`  
**기능**: 지원자 목록을 응답할 때 사용하는 모델
- `total_count`: 전체 지원자 수
- `applications`: 지원자 목록 (ApplicationListItem 배열)
- `page`: 현재 페이지
- `size`: 페이지 크기

#### ApplicationDetailResponse
**위치**: `schemas.py`  
**기능**: 지원서 상세 정보를 응답할 때 사용하는 모델
- `application_id`: 지원서 ID
- `applicant_id`: 지원자 ID
- `applicant_nickname`: 지원자 닉네임
- `status`: 지원서 상태
- `submitted_at`: 제출일
- `questions`: 질문과 답변 목록

#### ApplicationStatusUpdate
**위치**: `schemas.py`  
**기능**: 지원서 상태를 변경할 때 사용하는 요청 모델
- `new_status`: 새로운 상태

#### ApplicationStatusResponse
**위치**: `schemas.py`  
**기능**: 지원서 상태 변경 결과를 응답할 때 사용하는 모델
- `application_id`: 지원서 ID
- `status`: 변경된 상태
- `updated_at`: 변경일

### 🕐 기타

#### MeetingTime
**위치**: `schemas.py`  
**기능**: 미팅 시간을 정의하는 모델
- `day`: 요일 (월, 화, 수, 목, 금, 토, 일)
- `time`: 시간 (HH:MM 형식)

#### SignupForm
**위치**: `routers/auth.py`  
**기능**: 회원가입 시 사용하는 폼 모델
- `signup_token`: 회원가입 토큰
- `nickname`: 닉네임
- `track`: 트랙 (frontend, backend, plan, design, data)
- `school`: 학교명
- `portfolio_url`: 포트폴리오 URL (선택사항)

---

## 🌐 API 엔드포인트들

### 🔐 인증 관련
```
GET  /v1/auth/login/{provider}     # 소셜 로그인 시작 (kakao, naver, google)
GET  /v1/auth/{provider}/callback  # 소셜 로그인 콜백 처리
POST /v1/auth/signup               # 회원가입 완료
GET  /v1/auth/me                   # 현재 사용자 정보 조회
```

### 📝 공고 관련
```
GET  /v1/posts                     # 공고 목록 조회
POST /v1/posts                     # 공고 생성
GET  /v1/posts/{post_id}           # 공고 상세 조회
GET  /v1/posts/options             # 공고 작성 옵션 조회
```

### ❓ 질문 관련
```
GET  /v1/posts/{post_id}/questions # 공고 질문 조회
POST /v1/posts/{post_id}/questions # 공고 질문 생성
```

### 📄 지원서 관련
```
POST /v1/applications              # 지원서 제출
GET  /v1/applications/{id}         # 지원서 조회 (본인)
GET  /v1/posts/{post_id}/applications # 지원자 목록 조회 (모집자)
GET  /v1/applications/{id}/detail  # 지원서 상세 조회
PATCH /v1/applications/{id}/status # 지원서 상태 변경
```

### 🏥 헬스체크
```
GET  /ping                         # 핑 체크
HEAD /ping                         # 핑 체크 (HEAD)
GET  /health                       # 헬스 체크
HEAD /health                       # 헬스 체크 (HEAD)
```

---

## 🗄️ 데이터베이스 모델들

### 📊 Post
**위치**: `database.py`  
**기능**: 공고 정보를 저장하는 데이터베이스 모델
- `id`: 공고 ID (Primary Key)
- `user_id`: 작성자 ID (Foreign Key)
- `image_url`: 공고 이미지 URL
- `title`: 공고 제목
- `description`: 공고 설명
- `recruitment_field`: 모집 분야
- `recruitment_headcount`: 모집 인원
- `school_specific`: 학교 특정 여부
- `target_school_name`: 대상 학교명
- `deadline`: 마감일
- `external_link`: 외부 링크
- `created_at`: 생성일
- `updated_at`: 수정일
- `views`: 조회수

### 👤 User
**위치**: `database.py`  
**기능**: 사용자 정보를 저장하는 데이터베이스 모델
- `id`: 사용자 ID (Primary Key)
- `email`: 이메일
- `nickname`: 닉네임
- `track`: 트랙
- `school`: 학교명
- `portfolio_url`: 포트폴리오 URL
- `is_onboarded`: 온보딩 완료 여부
- `created_at`: 가입일
- `updated_at`: 수정일

### ❓ PostQuestion
**위치**: `database.py`  
**기능**: 공고의 커스터마이징 질문을 저장하는 데이터베이스 모델
- `id`: 질문 ID (Primary Key)
- `post_id`: 공고 ID (Foreign Key)
- `question_type`: 질문 타입
- `question_content`: 질문 내용
- `is_required`: 필수 여부
- `choices`: 선택지 목록 (JSON)
- `created_at`: 생성일

### 📄 Application
**위치**: `database.py`  
**기능**: 지원서 정보를 저장하는 데이터베이스 모델
- `id`: 지원서 ID (Primary Key)
- `post_id`: 공고 ID (Foreign Key)
- `applicant_id`: 지원자 ID (Foreign Key)
- `status`: 지원서 상태
- `created_at`: 제출일
- `updated_at`: 수정일

### ✍️ ApplicationAnswer
**위치**: `database.py`  
**기능**: 지원서의 질문 답변을 저장하는 데이터베이스 모델
- `id`: 답변 ID (Primary Key)
- `application_id`: 지원서 ID (Foreign Key)
- `post_question_id`: 질문 ID (Foreign Key)
- `answer_content`: 답변 내용
- `created_at`: 작성일

### 📋 ApplicationStatusLog
**위치**: `database.py`  
**기능**: 지원서 상태 변경 이력을 저장하는 데이터베이스 모델
- `id`: 로그 ID (Primary Key)
- `application_id`: 지원서 ID (Foreign Key)
- `old_status`: 이전 상태
- `new_status`: 새로운 상태
- `changed_by`: 변경자 ID (Foreign Key)
- `created_at`: 변경일

---

## 🔗 관계도

```
User (1) ←→ (N) Post
Post (1) ←→ (N) PostQuestion
Post (1) ←→ (N) Application
Application (1) ←→ (N) ApplicationAnswer
PostQuestion (1) ←→ (N) ApplicationAnswer
Application (1) ←→ (N) ApplicationStatusLog
User (1) ←→ (N) Application (지원자)
User (1) ←→ (N) ApplicationStatusLog (변경자)
```

이 가이드를 참고하여 프론트엔드와 백엔드의 컴포넌트명을 일치시키면 됩니다! 🚀
