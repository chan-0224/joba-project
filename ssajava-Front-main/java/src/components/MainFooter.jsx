import react, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useLocation, useNavigate } from 'react-router-dom';
import './MainFooter.css';

import home_icon1 from '../pages/Home/Home_images/home-icon1.png';
import home_icon2 from '../pages/Home/Home_images/home-icon2.png';

import profile_icon1 from '../pages/Home/Home_images/profile-icon1.png';
import profile_icon2 from '../pages/Home/Home_images/profile-icon2.png';

import mypage_icon1 from '../pages/Home/Home_images/mypage-icon1.png';
import mypage_icon2 from '../pages/Home/Home_images/mypage-icon2.png';

import advertise_icon1 from '../pages/Home/Home_images/advertise-icon1.png'; 
// import advertise_icon2 from '../pages/Home/Home_images/advertise-icon2.png'; 

import mentoring_icon1 from '../pages/Home/Home_images/mentoring-icon1.png'; 
// import mentoring_icon2 from '../pages/Home/Home_images/mentoring-icon2.png'; 

function MainFooter() {
  const location = useLocation();
  const navigate = useNavigate();
  const isHome = location.pathname === '/home';
  const isProfile = location.pathname === '/profile' || location.pathname === '/edit-profile' || location.pathname.startsWith('/profile/');
  const isMypage = location.pathname === '/mypage' || location.pathname === '/announcements' || location.pathname.startsWith('/announcements/') || location.pathname === '/application-history' || location.pathname === '/recruitment-history' || location.pathname.startsWith('/posts/') || location.pathname.startsWith('/applications/');
  //const isAdvertise = location.pathname === '/advertise';

  return (
    <div className="main-footer">
        <div className="main-footer-content">
            <div className="main-footer-home" onClick={() => navigate('/home')}>
                <img src={isHome ? home_icon2 : home_icon1} alt="홈 아이콘" className="main-footer-icon-home" />
                <span className={isHome ? 'footer-text-active' : 'footer-text'}>홈</span>
            </div>
            <div className="main-footer-profile" onClick={() => navigate('/profile')}>
                <img src={isProfile ? profile_icon2 : profile_icon1} alt="프로필 아이콘" className="main-footer-icon-profile" />
                <span className={isProfile ? 'footer-text-active' : 'footer-text'}>프로필</span>
            </div>
            <div className="main-footer-mypage" onClick={() => navigate('/mypage')}>
                <img src={isMypage ? mypage_icon2 : mypage_icon1} alt="마이페이지 아이콘" className="main-footer-icon-mypage" />
                <span className={isMypage ? 'footer-text-active' : 'footer-text'}>마이페이지</span>
            </div>
            <div className="main-footer-advertise">
                <img src={advertise_icon1} alt="공고 아이콘" className="main-footer-icon-advertise" />
                <span className="footer-text">공고</span>
            </div>
            <div className="main-footer-mentoring" >
                <img src={mentoring_icon1} alt="멘토링 아이콘" className="main-footer-icon-mentoring" />
                <span className="footer-text">멘토링</span>
            </div>
        </div>
    </div>
  );
}
export default MainFooter;