// src/pages/MyPage/ApplicantListPage.jsx

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../api/client';

import arrowRight from '../MyPage/images/arrow_right_ios.png';
import dotIcon from '../MyPage/images/dot.png';

import RecruitmentHistoryHeader from '../../components/RecruitmentHistoryHeader';

import './ApplicantListPage.css';

// 임시 데이터
const MOCK_APPLICANTS = [
  { application_id: 101, applicant: { user_id: 'kakao_123', name: '김철수', avatar_url: null, university: '백석대학교', field: '프론트엔드' }},
  { application_id: 102, applicant: { user_id: 'kakao_456', name: '박문희', avatar_url: null, university: '강남대학교', field: '프론트엔드' }},
  { application_id: 103, applicant: { user_id: 'kakao_789', name: '최윤하', avatar_url: null, university: '서울여자대학교', field: '프론트엔드' }},
];

function ApplicantListPage() {
  const navigate = useNavigate();
  const { postId } = useParams();
  const [applicants, setApplicants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchApplicants = async () => {
      if (!postId) return;
      try {
        setLoading(true);
        /*
          // --- API 호출 부분 주석 처리 ---
          const response = await api.get(`/posts/${postId}/applications`);
          setApplicants(response.data);
        */
        // --- Mock Data 사용 ---
        setApplicants(MOCK_APPLICANTS);
        
      } catch (error) {
        console.error("지원자 목록을 불러오는 데 실패했습니다.", error);
      } finally {
        setLoading(false);
      }
    };
    fetchApplicants();
  }, [postId]);

  if (loading) {
    return <div>지원자 목록을 불러오는 중...</div>;
  }

  return (
    <>
      <RecruitmentHistoryHeader />
    <div className="applicant-list-page">
      <header className="applicant-header">
        <div className="applicant-count-badge">
          {applicants.length}명 지원 중
        </div>
      </header>
      <main className="applicant-list">
        {applicants.length > 0 ? applicants.map(({ application_id, applicant }) => (
          <div key={application_id} className="applicant-item">
            <div className="applicant-info" onClick={() => navigate(`/profile/${applicant.user_id}`)}>
              <h4>{applicant.name}</h4>
              <p>
                <span>{applicant.field}</span>
                <span className="dot-divider">
                  <img src={dotIcon} alt="·" className="dot-icon" />
                </span>
                <span>{applicant.university}</span>
              </p>
            </div>
            <div className="view-application-link" onClick={() => navigate(`/applications/${application_id}/detail`)}>
              <span>지원서 확인</span>
              <img src={arrowRight} alt=">" className="view-arrow-icon" />
            </div>
          </div>
        )) : <p className="no-applicants">아직 지원자가 없습니다.</p>}
      </main>
      
      <footer className="applicant-footer-note">
        *이름 클릭 시 지원자의 프로필로 이동합니다.
      </footer>
    </div>
    </>
  );
}

export default ApplicantListPage;