import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/client';
import useLongPress from './useLongPress'; // 잠시 후 생성할 커스텀 훅
import ResultModal from './ResultModal'; // 잠시 후 생성할 모달 컴포넌트

import downIcon from './images/arrow_down_ios.png';
import pinkfire from '../Home/Home_images/pinkfire.png';
import './ApplicationHistoryPage.css';

// --- 실제 API 연동 전 사용할 임시 데이터 ---
const MOCK_APPLICATIONS = [
  {
    application_id: 101, status: "합격", result_link: "https://open.kakao.com/...",
    post: { post_id: 1, image_url: "/Home/Home_images/job1.jpg", title: "[삼육대] SW경진대회 UIUX 파트 모집", description: "2025년 SW경진대회 함께할 UIUX 디자이너...", current_applicants: 17, recruitment_headcount: 2 }
  },
  {
    application_id: 102, status: "제출됨",
    post: { post_id: 2, image_url: "/Home/Home_images/job2.jpg", title: "KOICA 활용 챌린지 함께할 디자이너 모집", description: "KOICA DATS를 활용한 챌린지에 참여할 디자이너...", current_applicants: 31, recruitment_headcount: 4 }
  },
  {
    application_id: 103, status: "불합격",
    post: { post_id: 3, image_url: "/Home/Home_images/job3.jpg", title: "관광데이터 공모전 디자이너 구합니다", description: "데이터 전문가와 함께 관광 데이터 공모전에...", current_applicants: 4, recruitment_headcount: 1 }
  },
];
// -----------------------------------------


function ApplicationHistoryPage() {
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState(null); // 모달에 띄울 지원서

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true);
        // TODO: 아래 API 주석을 풀고 실제 엔드포인트로 교체하세요.
        // const response = await api.get('/applications/me');
        // setApplications(response.data);
        
        // --- 임시 데이터 사용 ---
        setApplications(MOCK_APPLICATIONS);
        // -----------------------

      } catch (error) {
        console.error("지원 내역을 불러오는 데 실패했습니다.", error);
        alert("지원 내역을 불러오는 중 오류가 발생했습니다.");
      } finally {
        setLoading(false);
      }
    };
    fetchApplications();
  }, []);

  // 지원 취소 성공 시, 화면에서 해당 항목을 제거하는 함수
  const handleCancelSuccess = (applicationId) => {
    setApplications(prev => prev.filter(app => app.application_id !== applicationId));
    setSelectedApp(null); // 모달 닫기
  };

  if (loading) {
    return <div>로딩 중...</div>;
  }

  return (
    <>
      <div className="app-history-container">        
        <nav className="app-history-filter">
          <div className="filter-label-container">
            <div className="filter-label">지원 공고</div>&nbsp;
            <div className="filter-count">{applications.length}</div>
            <div className="filter-unit">개</div>
          </div>
          <div className="sort-dropdown">
            <span>최근순</span>
            <img src={ downIcon } className="sort-dropdown-icon"/>
          </div>
        </nav>

        <main className="app-history-list">
          {applications.map(app => (
            <ApplicationItem 
              key={app.application_id} 
              application={app}
              onShortPress={() => setSelectedApp(app)}
            />
          ))}
        </main>
      </div>
      
      {selectedApp && (
        <ResultModal 
          application={selectedApp}
          onClose={() => setSelectedApp(null)}
          onCancelSuccess={handleCancelSuccess}
        />
      )}
    </>
  );
}

function ApplicationItem({ application, onShortPress }) {
  const navigate = useNavigate();
  
  const longPressEvents = useLongPress(
    onShortPress, // 짧게 누르기 콜백
    () => navigate(`/posts/${application.post.post_id}`), // 길게 누르기 콜백
    { delay: 500 }
  );

  const isRejected = application.status === '불합격';

  return (
    <div 
      className={`application-item ${isRejected ? 'rejected' : ''}`}
      {...longPressEvents}
    >
      <div className="post-image">
        <img src={application.post.image_url} alt={application.post.title} className="post-image" />
      </div>
      <div className="post-info">
        <h3 className="post-title">{application.post.title}</h3>
        <p className="post-description">{application.post.description}</p>
        <div className="post-meta">
          <span className="meta-applicants">
            <img src={pinkfire} alt="지원자" className="meta-icon" />
            {application.post.current_applicants}명 지원 중
          </span>
          <span className="meta-headcount">
            {application.post.recruitment_headcount}명 모집
          </span>
        </div>
      </div>
      {isRejected && <div className="rejected-overlay">거절된 공고입니다.</div>}
    </div>
  );
}

export default ApplicationHistoryPage;