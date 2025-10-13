// src/pages/MyPage/ApplicationViewPage.jsx

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../api/client';
import ResultConfirmationModal from './ResultConfirmationModal';
import './ApplicationViewPage.css';

// 임시 데이터
const MOCK_APPLICATION_DETAIL = {
  applicant: { name: '김지원', university: 'A대학교', field: '프론트엔드' },
  answers: [
    { question: '1. 해당 공고에 지원한 동기를 작성해주세요.', answer: '평소 UIUX에 관심이 많아 지원하게 되었습니다. 이 프로젝트를 통해 사용자 중심의 디자인 설계를 경험하고 싶습니다.' },
    { question: '2. 가장 자신있는 역량을 어필해주세요.', answer: 'Figma를 활용한 프로토타이핑에 강점이 있습니다. 또한, 사용자 리서치를 통해 얻은 인사이트를 디자인에 반영하는 것을 즐깁니다.' },
  ]
};

function ApplicationViewPage() {
  const navigate = useNavigate();
  const { applicationId } = useParams();
  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const fetchApplication = async () => {
      if (!applicationId) return;
      try {
        setLoading(true);
        /*
          // --- API 호출 부분 주석 처리 ---
          const response = await api.get(`/v1/applications/${applicationId}/detail`);
          setApplication(response.data);
        */
        // --- Mock Data 사용 ---
        setApplication(MOCK_APPLICATION_DETAIL);

      } catch (error) {
        console.error("지원서 상세 정보를 불러오는 데 실패했습니다.", error);
      } finally {
        setLoading(false);
      }
    };
    fetchApplication();
  }, [applicationId]);

  if (loading || !application) {
    return <div>지원서 정보를 불러오는 중...</div>;
  }

  return (
    <>
      <div className="application-view-page">
        <header className="application-view-header">
          <img src="/close-btn.png" alt="닫기" onClick={() => navigate(-1)} />
        </header>
        <main className="application-content">
          {application.answers.map((item, index) => (
            <div key={index} className="qa-item">
              <h2>{item.question}</h2>
              <p>{item.answer}</p>
            </div>
          ))}
        </main>
        <footer className="application-view-footer">
          <button onClick={() => setIsModalOpen(true)}>결과 전송하기</button>
        </footer>
      </div>
      {isModalOpen && (
        <ResultConfirmationModal 
          applicationId={applicationId}
          applicant={application.applicant}
          onClose={() => setIsModalOpen(false)}
          onSuccess={() => navigate(-1)} // 성공 시 지원자 목록으로 돌아가기
        />
      )}
    </>
  );
}

export default ApplicationViewPage;