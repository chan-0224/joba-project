# JOBA Frontend API 명세서

## 📋 개요
JOBA 백엔드 API의 프론트엔드 연동을 위한 상세 명세서입니다.

## 🔗 기본 정보
- **Base URL**: `https://joba-project.onrender.com`
- **API Prefix**: `/v1`
- **Content-Type**: `application/json`
- **인증 방식**: JWT Bearer Token

## ⚠️ 중요: API 경로 구조
**모든 API 엔드포인트는 `/v1`으로 시작합니다.**

### 올바른 URL 예시:
- ✅ `https://joba-project.onrender.com/v1/posts` (공고 목록)
- ✅ `https://joba-project.onrender.com/v1/applications` (지원서 목록)
- ✅ `https://joba-project.onrender.com/v1/profile/{user_id}` (프로필 조회)
- ✅ `https://joba-project.onrender.com/v1/auth/login/kakao` (카카오 로그인)

### 잘못된 URL 예시:
- ❌ `https://joba-project.onrender.com/v1/posts/posts` (중복)
- ❌ `https://joba-project.onrender.com/v1/applications/applications` (중복)
- ❌ `https://joba-project.onrender.com/v1/auth/auth/login/kakao` (중복)

## 🔐 인증 (Authentication)

### 소셜 로그인
- **카카오 로그인**: `GET /v1/auth/login/kakao?frontRedirect={url}`
- **카카오 콜백**: `GET /v1/auth/kakao/callback` (302 리다이렉트)
- **네이버 로그인**: `GET /v1/auth/login/naver?frontRedirect={url}`
- **네이버 콜백**: `GET /v1/auth/naver/callback` (302 리다이렉트)
- **구글 로그인**: `GET /v1/auth/login/google?frontRedirect={url}`
- **구글 콜백**: `GET /v1/auth/google/callback` (302 리다이렉트)

### JWT 토큰
- **사용자 정보 조회**: `GET /v1/auth/me` (토큰 검증 포함)

### 회원가입
- **회원가입 완료**: `POST /v1/auth/signup` (온보딩 정보 입력)

## 📝 공고 (Posts)

### 공고 관리
- **공고 생성**: `POST /v1/posts` (이미지 업로드 포함)
- **공고 목록**: `GET /v1/posts` (필터링, 정렬, 검색, 페이지네이션 지원)
- **공고 상세**: `GET /v1/posts/{post_id}` (지원자 수, 모집된 인원 수, 모집 상태 포함)
- **공고 수정**: `PUT /v1/posts/{post_id}` (미구현)
- **공고 삭제**: `DELETE /v1/posts/{post_id}` (미구현)

### 공고 옵션 (프론트엔드 하드코딩)
⚠️ **중요**: 공고 작성 시 사용할 옵션들은 백엔드 API에서 제공하지 않습니다.
프론트엔드에서 다음 상수들을 사용하세요:

```javascript
const RECRUITMENT_FIELDS = ["프론트엔드", "백엔드", "기획", "디자인", "데이터 분석"];
const RECRUITMENT_HEADCOUNTS = ["1~2인", "3~5인", "6~10인", "인원미정"];
```

### 공고 질문 (커스터마이징)
- **질문 생성**: `POST /v1/posts/{post_id}/questions` (공고 작성자만)
- **질문 조회**: `GET /v1/posts/{post_id}/questions`

⚠️ **질문 타입**: TEXT, TEXTAREA, CHOICES, ATTACHMENT 지원
⚠️ **덮어쓰기**: 기존 질문 삭제 후 새로 생성

## 📋 지원서 (Applications)

### 지원서 관리
- **지원서 제출**: `POST /v1/applications` (커스터마이징된 질문 답변 포함)
- **지원서 상세 조회**: `GET /v1/applications/{application_id}` (본인만)
- **지원서 상세 조회 (모집자용)**: `GET /v1/applications/{application_id}/detail`
- **지원서 상태 변경**: `PATCH /v1/applications/{application_id}/status` (모집자만)
- **지원서 취소**: `PATCH /v1/applications/{application_id}/cancel` (지원자만)

### 지원자 관리 (모집자용)
- **공고별 지원자 목록**: `GET /v1/posts/{post_id}/applications` (페이지네이션, 필터링, 정렬 지원)

## 👤 프로필 (Profile)

### 프로필 관리
- **프로필 조회**: `GET /v1/profile/{user_id}`
- **프로필 수정**: `PUT /v1/profile/{user_id}` (Form 데이터 + 이미지 업로드)
- **시간표 업로드**: `POST /v1/profile/{user_id}/upload/timetable`

## 🚀 CORS 설정
백엔드는 다음 오리진에서의 요청을 허용합니다:
- `http://localhost:5173` (로컬 개발용)
- `http://localhost:3000` (로컬 개발용)
- `http://localhost:8080` (로컬 개발용)
- `https://ssajava-front.vercel.app` (프론트엔드 배포 URL)

## 🧩 프론트엔드 컴포넌트 가이드

### 📱 페이지 컴포넌트명
```javascript
// 페이지 컴포넌트
const PostsPage = () => { /* 공고 목록 페이지 */ }
const PostDetailPage = () => { /* 공고 상세 페이지 */ }
const CreatePostPage = () => { /* 공고 작성 페이지 */ }
const EditPostPage = () => { /* 공고 수정 페이지 */ }
const ApplicationsPage = () => { /* 지원서 목록 페이지 */ }
const ApplicationDetailPage = () => { /* 지원서 상세 페이지 */ }
const ProfilePage = () => { /* 사용자 프로필 페이지 */ }
const ProfileEditPage = () => { /* 프로필 수정 페이지 */ }
const LoginPage = () => { /* 로그인 페이지 */ }
```

### 🎨 UI 컴포넌트명
```javascript
// 공고 관련 컴포넌트
const PostCard = ({ post }) => { /* 공고 카드 */ }
const PostList = ({ posts }) => { /* 공고 목록 */ }
const PostForm = ({ onSubmit, initialData }) => { /* 공고 작성/수정 폼 */ }
const PostImage = ({ imageUrl, alt }) => { /* 공고 이미지 */ }
const PostActions = ({ post, onEdit, onDelete }) => { /* 공고 액션 버튼들 */ }

// 지원서 관련 컴포넌트
const ApplicationForm = ({ postId, questions, onSubmit }) => { /* 지원서 작성 폼 */ }
const ApplicationList = ({ applications }) => { /* 지원서 목록 */ }
const ApplicationCard = ({ application }) => { /* 지원서 카드 */ }
const ApplicationStatus = ({ status }) => { /* 지원서 상태 표시 */ }

// 질문 관련 컴포넌트
const QuestionList = ({ questions }) => { /* 질문 목록 */ }
const QuestionItem = ({ question, onChange }) => { /* 개별 질문 */ }
const QuestionForm = ({ onSubmit }) => { /* 질문 작성 폼 */ }

// 프로필 관련 컴포넌트
const ProfileCard = ({ profile }) => { /* 프로필 카드 */ }
const ProfileForm = ({ profile, onSubmit }) => { /* 프로필 수정 폼 */ }
const CareerList = ({ careers }) => { /* 경력 목록 */ }
const CareerForm = ({ career, onSubmit, onDelete }) => { /* 경력 폼 */ }
const ProfileImage = ({ imageUrl, type }) => { /* 프로필 이미지 (avatar, cover, timetable) */ }
const RecentProjects = ({ projects }) => { /* 최근 프로젝트 목록 */ }

// 인증 관련 컴포넌트
const LoginButtons = () => { /* 소셜 로그인 버튼들 */ }
const UserMenu = ({ user, onLogout }) => { /* 사용자 메뉴 */ }
const AuthGuard = ({ children }) => { /* 인증 필요 컴포넌트 */ }
```

### 🔧 API 호출 함수명
```javascript
// 공고 관련 API 함수
const getPosts = async (params) => { /* 공고 목록 조회 */ }
const getPost = async (id) => { /* 공고 상세 조회 */ }
const createPost = async (postData) => { /* 공고 생성 */ }
const updatePost = async (id, postData) => { /* 공고 수정 */ }
const deletePost = async (id) => { /* 공고 삭제 */ }
const searchPosts = async (searchParams) => { /* 공고 검색 */ }

// 공고 옵션 (프론트엔드 하드코딩)
const RECRUITMENT_FIELDS = ["프론트엔드", "백엔드", "기획", "디자인", "데이터 분석"];
const RECRUITMENT_HEADCOUNTS = ["1~2인", "3~5인", "6~10인", "인원미정"];

// 지원서 관련 API 함수
const getApplication = async (id) => { /* 지원서 상세 조회 (본인만) */ }
const getApplicationDetail = async (id) => { /* 지원서 상세 조회 (모집자용) */ }
const getPostApplications = async (postId, params) => { /* 공고별 지원자 목록 (모집자용) */ }
const submitApplication = async (applicationData, files) => { /* 지원서 제출 */ }
const updateApplicationStatus = async (id, status) => { /* 지원서 상태 변경 (모집자만) */ }
const cancelApplication = async (id) => { /* 지원서 취소 (지원자만) */ }

// 공고 질문 관련 API 함수
const getPostQuestions = async (postId) => { /* 공고 질문 조회 */ }
const createPostQuestions = async (postId, questions) => { /* 공고 질문 생성 */ }

// 프로필 관련 API 함수
const getProfile = async (userId) => { /* 프로필 조회 */ }
const updateProfile = async (userId, profileData) => { /* 프로필 수정 */ }
const uploadTimetable = async (userId, timetableFile) => { /* 시간표 업로드 */ }

// 인증 관련 API 함수
const kakaoLogin = () => { /* 카카오 로그인 */ }
const naverLogin = () => { /* 네이버 로그인 */ }
const googleLogin = () => { /* 구글 로그인 */ }
const completeSignup = async (signupData) => { /* 회원가입 완료 */ }
const getCurrentUser = async () => { /* 현재 사용자 정보 조회 (토큰 검증 포함) */ }
const logout = () => { /* 로그아웃 */ }
```

### 📊 상태 변수명
```javascript
// 공고 관련 상태
const [posts, setPosts] = useState([])                    // 공고 목록
const [currentPost, setCurrentPost] = useState(null)      // 현재 선택된 공고
const [postQuestions, setPostQuestions] = useState([])    // 공고 질문 목록
const [isLoadingPosts, setIsLoadingPosts] = useState(false) // 공고 로딩 상태
const [postError, setPostError] = useState(null)          // 공고 관련 에러

// 공고 옵션 상수 (프론트엔드 하드코딩)
const RECRUITMENT_FIELDS = ["프론트엔드", "백엔드", "기획", "디자인", "데이터 분석"];
const RECRUITMENT_HEADCOUNTS = ["1~2인", "3~5인", "6~10인", "인원미정"];

// 지원서 관련 상태
const [applications, setApplications] = useState([])      // 지원서 목록
const [currentApplication, setCurrentApplication] = useState(null) // 현재 선택된 지원서
const [isSubmitting, setIsSubmitting] = useState(false)   // 제출 중 상태

// 사용자 관련 상태
const [user, setUser] = useState(null)                    // 현재 사용자 정보
const [isAuthenticated, setIsAuthenticated] = useState(false) // 인증 상태
const [authToken, setAuthToken] = useState(null)          // 인증 토큰
const [isLoadingAuth, setIsLoadingAuth] = useState(false) // 인증 로딩 상태

// 프로필 관련 상태
const [profile, setProfile] = useState(null)              // 프로필 정보
const [careers, setCareers] = useState([])                // 경력 목록
const [recentProjects, setRecentProjects] = useState([])  // 최근 프로젝트
const [isUpdatingProfile, setIsUpdatingProfile] = useState(false) // 프로필 업데이트 중

// UI 상태
const [isModalOpen, setIsModalOpen] = useState(false)     // 모달 열림 상태
const [currentPage, setCurrentPage] = useState(1)         // 현재 페이지
const [searchQuery, setSearchQuery] = useState('')        // 검색 쿼리
const [selectedFilters, setSelectedFilters] = useState({}) // 선택된 필터들
```

### 🎯 이벤트 핸들러명
```javascript
// 공고 관련 이벤트 핸들러
const handleCreatePost = async (postData) => { /* 공고 생성 처리 */ }
const handleUpdatePost = async (id, postData) => { /* 공고 수정 처리 */ }
const handleDeletePost = async (id) => { /* 공고 삭제 처리 */ }
const handlePostSearch = async (searchParams) => { /* 공고 검색 처리 */ }
const handlePostFilter = (filters) => { /* 공고 필터 처리 */ }
const handlePostSort = (sortBy) => { /* 공고 정렬 처리 */ }

// 지원서 관련 이벤트 핸들러
const handleSubmitApplication = async (applicationData) => { /* 지원서 제출 처리 */ }
const handleUpdateApplicationStatus = async (id, status) => { /* 지원서 상태 변경 처리 */ }
const handleApplicationCancel = async (id) => { /* 지원서 취소 처리 */ }

// 프로필 관련 이벤트 핸들러
const handleProfileUpdate = async (profileData) => { /* 프로필 수정 처리 */ }
const handleCareerAdd = (careerData) => { /* 경력 추가 처리 */ }
const handleCareerEdit = (id, careerData) => { /* 경력 수정 처리 */ }
const handleCareerDelete = (id) => { /* 경력 삭제 처리 */ }
const handleImageUpload = async (file, type) => { /* 이미지 업로드 처리 */ }

// 인증 관련 이벤트 핸들러
const handleKakaoLogin = () => { /* 카카오 로그인 처리 */ }
const handleNaverLogin = () => { /* 네이버 로그인 처리 */ }
const handleGoogleLogin = () => { /* 구글 로그인 처리 */ }
const handleLogout = () => { /* 로그아웃 처리 */ }

// UI 관련 이벤트 핸들러
const handleModalOpen = () => { /* 모달 열기 */ }
const handleModalClose = () => { /* 모달 닫기 */ }
const handlePageChange = (page) => { /* 페이지 변경 */ }
const handleSearchSubmit = (query) => { /* 검색 제출 */ }
const handleFilterChange = (filterType, value) => { /* 필터 변경 */ }
```

### 🎨 스타일 클래스명
```css
/* 공고 관련 스타일 */
.post-card { /* 공고 카드 스타일 */ }
.post-list { /* 공고 목록 스타일 */ }
.post-form { /* 공고 폼 스타일 */ }
.post-image { /* 공고 이미지 스타일 */ }
.post-actions { /* 공고 액션 버튼 스타일 */ }

/* 지원서 관련 스타일 */
.application-form { /* 지원서 폼 스타일 */ }
.application-list { /* 지원서 목록 스타일 */ }
.application-card { /* 지원서 카드 스타일 */ }
.application-status { /* 지원서 상태 스타일 */ }

/* 질문 관련 스타일 */
.question-list { /* 질문 목록 스타일 */ }
.question-item { /* 질문 아이템 스타일 */ }
.question-form { /* 질문 폼 스타일 */ }

/* 프로필 관련 스타일 */
.profile-card { /* 프로필 카드 스타일 */ }
.profile-form { /* 프로필 폼 스타일 */ }
.career-list { /* 경력 목록 스타일 */ }
.career-item { /* 경력 아이템 스타일 */ }
.profile-image { /* 프로필 이미지 스타일 */ }
.recent-projects { /* 최근 프로젝트 스타일 */ }

/* 인증 관련 스타일 */
.login-buttons { /* 로그인 버튼들 스타일 */ }
.user-menu { /* 사용자 메뉴 스타일 */ }
.auth-guard { /* 인증 가드 스타일 */ }

/* 공통 스타일 */
.loading { /* 로딩 상태 스타일 */ }
.error { /* 에러 상태 스타일 */ }
.success { /* 성공 상태 스타일 */ }
.disabled { /* 비활성화 상태 스타일 */ }
```

## 📊 지원서 상태 관리

### 지원서 상태 종류
- **제출됨**: 초기 지원 상태
- **열람됨**: 모집자가 상세 조회한 상태 (자동 변경 - 현재 미사용)
- **합격**: 모집자가 합격 처리
- **불합격**: 모집자가 불합격 처리  
- **취소됨**: 지원자가 직접 취소

### 상태 변경 규칙
- 지원자: "제출됨" → "취소됨"만 가능
- 모집자: "제출됨" → "합격"/"불합격" 가능
- 최종 상태("합격", "불합격")에서는 더 이상 변경 불가

## 📱 사용 예시

### 회원가입 플로우
```javascript
// 1. 소셜 로그인 후 신규 사용자인 경우
// frontRedirect에서 requires_signup=true와 signup_token 받음

// 2. 회원가입 완료 요청 (신규 키만 사용)
const signupData = {
  signup_token: token,         // 소셜 로그인 시 발급받은 토큰
  email: email,                // 미리 채워진 이메일(선택)
  name: name,                  // 사용자가 직접 입력한 이름
  field: field,                // 사용자가 선택한 트랙 (frontend|backend|plan|design|data)
  university: univ,            // 사용자가 직접 입력한 학교
  portfolio: portfolio || null // 포트폴리오(선택)
};

const response = await fetch('/v1/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(signupData)
});

const result = await response.json();
// { "access_token": "jwt토큰", "user_id": "사용자ID" }
```

### 소셜 로그인 요청
```javascript
// 카카오 로그인 (올바른 방법)
const frontRedirect = encodeURIComponent('http://localhost:5173/oauth/callback/kakao');
const kakaoLoginUrl = `https://joba-project.onrender.com/v1/auth/login/kakao?frontRedirect=${frontRedirect}`;

// 네이버 로그인 (올바른 방법)
const naverLoginUrl = `https://joba-project.onrender.com/v1/auth/login/naver?frontRedirect=${frontRedirect}`;

// 구글 로그인 (올바른 방법)
const googleLoginUrl = `https://joba-project.onrender.com/v1/auth/login/google?frontRedirect=${frontRedirect}`;

// 잘못된 방법 (중복 경로)
const wrongUrl = 'https://joba-project.onrender.com/v1/auth/auth/login/kakao';
```

### 공고 목록 요청 (필터링 및 정렬)
```javascript
// 기본 목록 조회
const postsUrl = 'https://joba-project.onrender.com/v1/posts';

// 필터링 및 정렬 옵션
const params = new URLSearchParams({
  sort: '최신순', // 허용값: 최신순|인기순|랜덤순
  recruitment_field: '프론트엔드', // 선택사항
  recruitment_headcount: '3~5인', // 선택사항
  school_name: '서울대학교', // 선택사항
  q: '검색키워드', // 선택사항
  page: '1',
  size: '10'
});

const filteredUrl = `${postsUrl}?${params}`;

// 응답 예시
{
  "total_count": 10,
  "posts": [
    {
      "id": 1,
      "user_id": "kakao_123456789",
      "title": "프론트엔드 개발자 모집",
      "recruitment_field": "프론트엔드",
      "recruitment_headcount": "3~5인",
      "application_count": 8,
      "recruited_count": 2,
      "recruitment_status": "모집중",
      "image_url": "https://storage.googleapis.com/...",
      "deadline": "2024-12-31T23:59:59",
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}

// 잘못된 방법 (중복 경로)
const wrongUrl = 'https://joba-project.onrender.com/v1/posts/posts';
```

### 지원서 제출 요청
```javascript
// 1. 공고 질문 조회
const questionsResponse = await fetch('/v1/posts/1/questions');
const questions = await questionsResponse.json();

// 2. 지원서 데이터 준비
const applicationData = {
  post_id: 1,
  answers: [
    {
      post_question_id: 1,
      answer_content: "저는 React와 TypeScript에 능숙합니다."
    },
    {
      post_question_id: 2,
      answer_content: "portfolio.pdf" // ATTACHMENT 타입인 경우 파일명
    }
  ]
};

// 3. FormData로 파일과 함께 전송 (ATTACHMENT 타입 질문이 있는 경우)
const formData = new FormData();
formData.append('application_data', JSON.stringify(applicationData));
formData.append('portfolio_files', portfolioFile); // 파일 객체

const response = await fetch('/v1/applications', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`
  },
  body: formData
});
```

### 프로필 조회 요청
```javascript
// 올바른 방법
const profileUrl = 'https://joba-project.onrender.com/v1/profile/kakao_12345';

// 응답 예시
{
  "user_id": "kakao_12345",
  "email": "user@example.com",
  "track": "프론트엔드",
  "school": "한국대학교",
  "portfolio_url": "https://portfolio.example.com",
  "avatar_url": "https://storage.googleapis.com/joba-bucket/profiles/kakao_12345/avatars/abc123.jpg",
  "cover_url": "https://storage.googleapis.com/joba-bucket/profiles/kakao_12345/covers/def456.jpg",
  "timetable_url": "https://storage.googleapis.com/joba-bucket/profiles/kakao_12345/timetables/ghi789.jpg",
  "careers": {
    "2024": [
      {"id": 1, "description": "SSAFY 11기 수료"}
    ],
    "2023": [
      {"id": 2, "description": "웹 개발 부트캠프 수료"}
    ]
  },
  "recent_projects": [
    {
      "id": 15,
      "title": "React 쇼핑몰 프로젝트",
      "image_url": "https://storage.googleapis.com/joba-bucket/posts/images/project1.jpg"
    }
  ]
}
```

### 프로필 수정 요청 (Form 데이터)
```javascript
// 올바른 방법 - FormData 사용 (이미지 포함)
const updateProfileWithImage = async (userId, profileData) => {
  const formData = new FormData();
  
  // 텍스트 데이터
  if (profileData.track) formData.append('track', profileData.track);
  if (profileData.school) formData.append('school', profileData.school);
  if (profileData.portfolio_url) formData.append('portfolio_url', profileData.portfolio_url);
  
  // 경력 데이터 (JSON 문자열)
  if (profileData.careers) {
    formData.append('careers', JSON.stringify(profileData.careers));
  }
  
  // 이미지 파일들
  if (profileData.avatar) formData.append('avatar', profileData.avatar);
  if (profileData.cover) formData.append('cover', profileData.cover);
  
  const response = await fetch(`/v1/profile/${userId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${authToken}`
    },
    body: formData
  });
  
  return response.json();
};

// 경력 데이터 예시
const careersData = [
  { "id": 1, "year": 2024, "description": "SSAFY 11기 수료" },
  { "year": 2023, "description": "웹 개발 부트캠프 수료" } // id 없으면 새로 생성
];
```

## 🔧 환경변수 설정
프론트엔드에서 다음 환경변수를 올바르게 설정하세요:

```bash
# 올바른 설정
VITE_API_BASE_URL=https://joba-project.onrender.com/v1

# 잘못된 설정 (중복 경로 포함)
VITE_API_BASE_URL=https://joba-project.onrender.com/v1/posts
```

## 📚 추가 리소스
- **Swagger UI**: `https://joba-project.onrender.com/docs`
- **ReDoc**: `https://joba-project.onrender.com/redoc`
- **GitHub**: 프로젝트 소스코드 및 이슈 트래킹 

## 🏠 홈 화면 연동

### 목표
- 사용자 닉네임/트랙 표시
- 공고 카드 목록(이미지, 제목, 지원자 수) 표시
- 로그인 사용자의 트랙에 따라 자동 필터링된 공고 노출
- “팀원 모집하기” 버튼 → 공고 작성 페이지로 이동

### 1) 사용자 정보 불러오기 (닉네임/트랙)
- 엔드포인트: `GET /v1/auth/me`
- 헤더: `Authorization: Bearer <token>`
- 주요 응답: `nickname`, `track`(한글: 프론트엔드/백엔드/기획/디자인/데이터 분석)

참고: 이 엔드포인트로 닉네임/트랙을 조회합니다.

### 2) 공고 목록 불러오기 (이미지/제목/지원자 수)
- 엔드포인트: `GET /v1/posts`
- 쿼리: `recruitment_field`(선택, 한글), `sort`, `page`, `size`
- 카드 표시용 필드: `image_url`, `title`, `application_count`, `recruitment_status`, `id`

참고: 사용자 트랙 값을 `recruitment_field` 쿼리에 사용하세요.

### 3) 팀원 모집하기 버튼 → 공고 작성
- 프론트 라우팅: 작성 페이지로 이동(e.g. `/posts/create`)
- 백엔드: `POST /v1/posts` (multipart/form-data)
  - 헤더: `Authorization: Bearer <token>`
  - 바디: `image_file`(필수 파일) + `title`, `description`, `recruitment_field`(한글), `recruitment_headcount`, `deadline` 등

참고: multipart/form-data로 이미지 파일과 필드를 전송합니다.

 