// src/pages/Announcements/AnnouncementsList.jsx

import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Announcements.css'; // CSS는 하나의 파일을 공유해서 사용합니다.

import arrowRight from '../MyPage/images/arrow_right_ios.png';

// 백엔드가 없으므로 임시로 사용할 공지사항 데이터입니다.
const announcementsData = [
  { id: 1, title: '자바 서비스 게시!', date: '2025 / 09 / 18', content: '자바를 이용해주셔서 감사합니다.\n드디어 여러분께 자바의 정식 버전을 공개합니다!\n\n자바에서 동료들을 모아 여러분들의 꿈을 펼쳐보세요!\n\n자세한 내용은 커뮤니티 공지를 참고 바랍니다.' },
  { id: 2, title: '서버 점검 안내', date: '2025 / 09 / 17', content: '보다 안정적인 서비스 제공을 위해 서버 점검을 진행할 예정입니다. 양해 부탁드립니다.' },
  { id: 3, title: '개인정보처리방침 개정 안내', date: '2025 / 09 / 16', content: '개인정보처리방침이 일부 개정되어 안내드립니다. 변경된 내용은 설정 페이지에서 확인하실 수 있습니다.' },
];

function AnnouncementsList() {
  const navigate = useNavigate();

  const handleBack = () => {
    // 브라우저 히스토리에 따라 뒤로가거나 온보딩으로 이동
    if (window.history.length > 2) navigate(-1);
    else navigate('/');
  };

  return (
    <div className="announcement-container">
      {/* 페이지 헤더 */}
      <div className="announcement-header">
        <img
            src="/arrow_back_ios.png"
            alt="뒤로가기"
            className="back-button"
            onClick={handleBack}
          />
        <div className="header-title">서비스 공지사항</div>
      </div>

      {/* 공지사항 목록 */}
      <div className="announcement-list">
        {announcementsData.map(item => (
          // 각 공지사항을 누르면 id값을 가지고 상세 페이지로 이동합니다.
          <div key={item.id} className="announcement-item" onClick={() => navigate(`/announcements/${item.id}`)}>
            <span className="item-title">{item.title}</span>
            <span className="item-link">
              <div>공지 확인</div>
              <img src={arrowRight} alt=">" className="announcement-arrow-icon" />
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AnnouncementsList;