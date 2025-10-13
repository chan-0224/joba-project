// src/pages/Announcements/AnnouncementDetail.jsx

import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './Announcements.css';

// 목록 페이지와 동일한 임시 데이터를 사용합니다.
const announcementsData = [
    { id: 1, title: '자바 서비스 게시!', date: '2025 / 09 / 18', content: '자바를 이용해주셔서 감사합니다.\n드디어 여러분께 자바의 정식 버전을 공개합니다!\n\n자바에서 동료들을 모아 여러분들의 꿈을 펼쳐보세요!\n\n자세한 내용은 커뮤니티 공지를 참고 바랍니다.' },
    { id: 2, title: '서버 점검 안내', date: '2025 / 09 / 17', content: '보다 안정적인 서비스 제공을 위해 서버 점검을 진행할 예정입니다. 양해 부탁드립니다.' },
    { id: 3, title: '개인정보처리방침 개정 안내', date: '2025 / 09 / 16', content: '개인정보처리방침이 일부 개정되어 안내드립니다. 변경된 내용은 설정 페이지에서 확인하실 수 있습니다.' },
];

function AnnouncementDetail() {
  const navigate = useNavigate();

  const handleBack = () => {
    // 브라우저 히스토리에 따라 뒤로가거나 온보딩으로 이동
    if (window.history.length > 2) navigate(-1);
    else navigate('/');
  };

  // URL에 포함된 id 값을 가져옵니다. (예: /announcements/1 -> id는 1)
  const { id } = useParams();
  
  // id 값과 일치하는 공지사항 데이터를 찾습니다.
  const announcement = announcementsData.find(item => item.id === parseInt(id));

  // 만약 해당 id의 공지사항이 없으면 "없음" 메시지를 표시합니다.
  if (!announcement) {
    return <div>공지사항을 찾을 수 없습니다.</div>;
  }

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

      {/* 공지사항 상세 내용 */}
      <div className="announcement-detail">
        <div className="detail-date">{announcement.date}</div>
        <h2 className="detail-title">{announcement.title}</h2>
        <div className="detail-separator" />
        <p className="detail-content">{announcement.content}</p>
      </div>
    </div>
  );
}

export default AnnouncementDetail;