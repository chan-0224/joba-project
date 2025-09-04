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
- ✅ `https://joba-project.onrender.com/v1/auth/login/kakao` (카카오 로그인)

### 잘못된 URL 예시:
- ❌ `https://joba-project.onrender.com/v1/posts/posts` (중복)
- ❌ `https://joba-project.onrender.com/v1/applications/applications` (중복)
- ❌ `https://joba-project.onrender.com/v1/auth/auth/login/kakao` (중복)

## 🔐 인증 (Authentication)

### 소셜 로그인
- **카카오 로그인**: `GET /v1/auth/login/kakao?frontRedirect={url}`
- **카카오 콜백**: `GET /v1/auth/kakao/callback` (302 리다이렉트)
- **네이버 로그인**: `GET /v1/auth/login/naver`
- **네이버 콜백**: `GET /v1/auth/naver/callback`
- **구글 로그인**: `GET /v1/auth/login/google`
- **구글 콜백**: `GET /v1/auth/google/callback`

### JWT 토큰
- **토큰 검증**: `GET /v1/auth/verify`
- **토큰 갱신**: `POST /v1/auth/refresh`

## 📝 공고 (Posts)

### 공고 관리
- **공고 생성**: `POST /v1/posts` (이미지 업로드 포함)
- **공고 목록**: `GET /v1/posts` (지원자 수, 모집된 인원 수, 모집 상태 포함)
- **공고 상세**: `GET /v1/posts/{post_id}` (지원자 수, 모집된 인원 수, 모집 상태 포함)
- **공고 옵션**: `GET /v1/posts/fields` (모집 분야, 모집 인원 옵션)
- **공고 수정**: `PUT /v1/posts/{post_id}`
- **공고 삭제**: `DELETE /v1/posts/{post_id}`

### 공고 질문
- **질문 생성**: `POST /v1/posts/{post_id}/questions`
- **질문 조회**: `GET /v1/posts/{post_id}/questions`

## 📋 지원서 (Applications)

### 지원서 관리
- **지원서 제출**: `POST /v1/applications`
- **지원서 목록**: `GET /v1/applications`
- **지원서 상세**: `GET /v1/applications/{application_id}`
- **지원서 상태 변경**: `PUT /v1/applications/{application_id}/status`

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
const getPostOptions = async () => { /* 공고 옵션 조회 */ }
const createPost = async (postData) => { /* 공고 생성 */ }
const updatePost = async (id, postData) => { /* 공고 수정 */ }
const deletePost = async (id) => { /* 공고 삭제 */ }
const searchPosts = async (searchParams) => { /* 공고 검색 */ }

// 지원서 관련 API 함수
const getApplications = async () => { /* 지원서 목록 조회 */ }
const getApplication = async (id) => { /* 지원서 상세 조회 */ }
const submitApplication = async (applicationData) => { /* 지원서 제출 */ }
const updateApplicationStatus = async (id, status) => { /* 지원서 상태 변경 */ }

// 공고 질문 관련 API 함수
const getPostQuestions = async (postId) => { /* 공고 질문 조회 */ }
const createPostQuestions = async (postId, questions) => { /* 공고 질문 생성 */ }

// 인증 관련 API 함수
const kakaoLogin = () => { /* 카카오 로그인 */ }
const naverLogin = () => { /* 네이버 로그인 */ }
const googleLogin = () => { /* 구글 로그인 */ }
const verifyToken = async () => { /* 토큰 검증 */ }
const refreshToken = async () => { /* 토큰 갱신 */ }
const logout = () => { /* 로그아웃 */ }
```

### 📊 상태 변수명
```javascript
// 공고 관련 상태
const [posts, setPosts] = useState([])                    // 공고 목록
const [currentPost, setCurrentPost] = useState(null)      // 현재 선택된 공고
const [postOptions, setPostOptions] = useState(null)      // 공고 옵션 (모집 분야, 인원)
const [postQuestions, setPostQuestions] = useState([])    // 공고 질문 목록
const [isLoadingPosts, setIsLoadingPosts] = useState(false) // 공고 로딩 상태
const [postError, setPostError] = useState(null)          // 공고 관련 에러

// 지원서 관련 상태
const [applications, setApplications] = useState([])      // 지원서 목록
const [currentApplication, setCurrentApplication] = useState(null) // 현재 선택된 지원서
const [isSubmitting, setIsSubmitting] = useState(false)   // 제출 중 상태

// 사용자 관련 상태
const [user, setUser] = useState(null)                    // 현재 사용자 정보
const [isAuthenticated, setIsAuthenticated] = useState(false) // 인증 상태
const [authToken, setAuthToken] = useState(null)          // 인증 토큰
const [isLoadingAuth, setIsLoadingAuth] = useState(false) // 인증 로딩 상태

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

## 📱 사용 예시

### 카카오 로그인 요청
```javascript
// 올바른 방법 (frontRedirect 파라미터 포함)
const frontRedirect = encodeURIComponent('http://localhost:5173/oauth/callback/kakao');
const loginUrl = `https://joba-project.onrender.com/v1/auth/login/kakao?frontRedirect=${frontRedirect}`;

// 잘못된 방법 (중복 경로)
const wrongUrl = 'https://joba-project.onrender.com/v1/auth/auth/login/kakao';
```

### 공고 목록 요청
```javascript
// 올바른 방법
const postsUrl = 'https://joba-project.onrender.com/v1/posts';

// 응답 예시
{
  "total_count": 10,
  "posts": [
    {
      "id": 1,
      "title": "프론트엔드 개발자 모집",
      "recruitment_headcount": "3~5인",
      "application_count": 8,
      "recruited_count": 2,
      "recruitment_status": "모집중"
    }
  ]
}

// 공고 옵션 조회 예시
const postOptions = {
  "recruitment_fields": ["프론트엔드", "백엔드", "기획", "디자인", "데이터 분석"],
  "recruitment_headcounts": ["1~2인", "3~5인", "6~10인", "인원미정"]
}

// 잘못된 방법 (중복 경로)
const wrongUrl = 'https://joba-project.onrender.com/v1/posts/posts';
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