import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

// 온보딩 및 Auth 관련 페이지
import Onboarding from "./pages/Onboarding/Onboarding";

// 1. AuthProvider 임포트
import { AuthProvider } from './contexts/AuthContext'; 

import Login from "./pages/Auth/Login";
import SignupHeader from "./components/SignupHeader";
import Signup from "./pages/Auth/Signup";
import Signup2 from "./pages/Auth/Signup2";
import ForgotPassword from "./pages/Auth/ForgotPassword";

// OAuth 콜백 페이지
import OAuthCallback from "./pages/Auth/OAuthCallback";

// 메인 기능 페이지
import MainPage from "./pages/Home/MainPage";
import MainFooter from "./components/MainFooter";
import DeveloperCard from './pages/Home/DeveloperCard';

// 마이페이지
import MyPageHeader from "./components/MyPageHeader";
import MyPage from "./pages/MyPage/MyPage";

// 마이페이지 지원내역
import ApplicationHistoryHeader from "./components/ApplicationHistoryHeader";
import ApplicationHistoryPage from "./pages/MyPage/ApplicationHistoryPage";

// 마이페이지 모집 내역
import RecruitmentHistoryHeader from './components/RecruitmentHistoryHeader';
import RecruitmentHistoryPage from "./pages/MyPage/RecruitmentHistoryPage";
import ApplicantListPage from "./pages/MyPage/ApplicantListPage";
import ApplicationViewPage from "./pages/MyPage/ApplicationViewPage";

// 마이페이지 공지사항
import AnnouncementsList from "./pages/Announcements/AnnouncementsList";
import AnnouncementDetail from "./pages/Announcements/AnnouncementDetail";

// 프로필 관련 페이지
import Profile from "./pages/Profiles/Profile";
import EditProfile from "./pages/Profiles/EditProfile";

// Pretendard 폰트 적용 (index.css에 설정했지롱)

ReactDOM.createRoot(document.getElementById('root')).render(

  <React.StrictMode>
    <AuthProvider>
    <Router>
      <Routes>
        {/* 온보딩 */}
        <Route path="/" element={<Onboarding />} />
        
        {/* Auth */}
        <Route path="/oauth/callback/:provider" element={<OAuthCallback />} />
        
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={
          <div className='signup-wrapper'>
            <SignupHeader />
            <Signup />
          </div>
        } />
        <Route path="/signup2" element={
          <div className='signup-wrapper'>
            <SignupHeader />
            <Signup2 />
          </div>
        } />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        {/* OAuth 콜백 */}
        <Route path="/oauth/callback/kakao" element={<OAuthCallback />} />
        <Route path="/oauth/callback/naver" element={<OAuthCallback />} /> 
        <Route path="/oauth/callback/google" element={<OAuthCallback />} />
        
        {/* 메인 */}
        <Route path="/home" element={
          <>
            <MainPage />
            <MainFooter />
          </>
        } />
        
        {/* 마이페이지 */}
        <Route path="/mypage" element={
          <>
            <MyPageHeader />
            <MyPage />
            <MainFooter />
          </>
        } />
        

        {/* 마이페이지 지원내역 */}
        <Route path="/application-history" element={
          <>
            <ApplicationHistoryHeader />
            <ApplicationHistoryPage />
            <MainFooter />
          </>
        } />

        {/* --- 모집 내역 관련 라우트 --- */}
        <Route path="/recruitment-history" element={
          <>
            {/* <RecruitmentHistoryHeader /> */}
            <RecruitmentHistoryPage />
            <MainFooter/>
          </>
        } />
        <Route path="/posts/:postId/applications" element={
          <>
            {/* <RecruitmentHistoryHeader /> */}
            <ApplicantListPage />
            <MainFooter/>
          </>
        } />
        <Route path="/applications/:applicationId/detail" element={
          <>
            {/* <RecruitmentHistoryHeader /> */}
            <ApplicationViewPage />
            <MainFooter/>
          </>
        } />

        {/* 마이페이지 공지사항 */}
        <Route path="/announcements" element={
          <>
            <AnnouncementsList />
            <MainFooter />
          </>} 
        />
        <Route path="/announcements/:id" element={
          <>
            <AnnouncementDetail />
            <MainFooter />
          </>}
         />

        {/* 프로필 */}
        {/* --- ✨ 프로필 라우트 통합 및 수정 ✨ --- */}
        {/* 1. /profile/:userId: 다른 사람 프로필 볼 때 사용 */}
        <Route path="/profile/:userId" element={
          <>
            <Profile />
            <MainFooter />
          </>
        } />
        <Route path="/profile" element={
          <>
            <Profile />
            <MainFooter />
          </>
          } />
        <Route path="/edit-profile" element={
          <>
            <EditProfile />
            {/* <MainFooter /> */}
          </>
          } />
      </Routes>
    </Router>
    </AuthProvider>
  </React.StrictMode>
);

