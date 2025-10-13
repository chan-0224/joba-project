// src/pages/Home/MainPage.jsx

import React, { useEffect, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext'; // 1. useAuth 훅 임포트

import fire from './Home_images/mainpage-title.png';
import bulb from './Home_images/mainpage-post.png';
import developer from './Home_images/mainpage-subtitle.png';
import mainpage_post_arrow from '/arrow_back_ios.png';
import job1 from './Home_images/job1.jpg';
import job2 from './Home_images/job2.jpg';
import job3 from './Home_images/job3.jpg';
import pinkfire from './Home_images/pinkfire.png';

import './MainPage.css';
import DeveloperCard from './DeveloperCard';

const TRACKS = [
  { id: '프론트엔드', label: '프론트엔드', icon: 'frontend.png', iconClass: 'imgfrontend', width: '129' },
  { id: '백엔드', label: '백엔드', icon: 'backend.png', iconClass: 'imgbackend', width: '101' },
  { id: '기획', label: '기획', icon: 'plan.png', iconClass: 'imgplan', width: '93' },
  { id: '디자인', label: '디자인', icon: 'design.png', iconClass: 'imgdesign', width: '104' },
  { id: '데이터 분석', label: '데이터 분석', icon: 'dataanalysis.png', iconClass: 'imgdataanalysis', width: '124' },
];

function MainPage() {
  const { user } = useAuth(); // 2. AuthContext에서 사용자 정보 바로 가져오기

  console.log("MainPage가 받은 user 데이터:", user); // user 객체 확인
  
  // 3. 사용자의 field를 기반으로 UI 상태 관리
  const [selectedField, setSelectedField] = useState(user?.field || '');

  // 4. 전역 user 상태가 변경되면, 페이지의 선택된 필드도 동기화
  useEffect(() => {
    if (user?.field) {
      setSelectedField(user.field);
    }
  }, [user?.field]);

  const sortedTracks = [...TRACKS];
  if (selectedField) {
    const index = sortedTracks.findIndex(track => track.label === selectedField);
    if (index > -1) {
      const selected = sortedTracks.splice(index, 1)[0];
      sortedTracks.unshift(selected);
    }
  }

  const jobs = [
    { image: job1, title: '[삼육대] SW경진대회 UIUX 파트 모집합니다', tag: pinkfire, applicants: 17, track: '디자인' },
    { image: job2, title: 'KOICA 활용 챌린지 함께하실 디자이너 모집', tag: pinkfire, applicants: 31, track: '디자인' },
    { image: job3, title: '관광데이터 공모전 디자이너 구합니다', tag: pinkfire, applicants: 4, track: '디자인' },
  ];

  const developers = [
    { name: '김지원', field: '프론트엔드', university: '삼육대학교', avatar: '/Home/dev-avatar1.png', background: '/Home/dev-bg1.png' },
    { name: '이준혁', field: '백엔드', university: '가천대', avatar: '/Home/dev-avatar2.png', background: '/Home/dev-bg2.png' },
    { name: '정수빈', field: '디자인', university: '홍익대학교', avatar: '/Home/dev-avatar3.png', background: '/Home/dev-bg1.png' },
  ];

  return (
    <div className="mainpage-container">
      <div className="mainpage-title-section">
        <div className="mainpage-title">
          {/* 5. user 객체에서 바로 name을 사용 */}
          <span className="mainpage-name">{user?.name || '사용자'}</span>님을 위한<br />
          맞춤형 <strong>추천 공고</strong>예요!
        </div>
        <img src={fire} alt="불" className="mainpage-title-fire" />
      </div>

      <div className="mainpage-categories">
        {sortedTracks.map((track) => (
          <button
            key={track.id}
            type="button"
            className={`category-button${selectedField === track.label ? ' active' : ''}`}
            style={{ width: `${track.width}px` }}
            onClick={() => setSelectedField(track.label)}
          >
            <img src={`/${track.icon}`} className={track.iconClass} alt={track.label + " 아이콘"} />
            <span className="category-button-text">{track.label}</span>
          </button>
        ))}
      </div>


      <div className="mainpage-scroll-cards">
        {jobs.map((job, i) => (
          <div key={i} className="mainpage-card">
            <img src={job.image} alt={job.title} className="mainpage-card-img" />
            <div className="mainpage-card-title">{job.title}</div>
            <div className="mainpage-card-footer">
              <img src={job.tag} alt="태그" className="mainpage-card-tag" />
              <span className="mainpage-card-applicants">{job.applicants}명 지원 중</span>
            </div>
          </div>
        ))}
      </div>

      <button className="mainpage-post-button">
        <img src={bulb} alt="전구" className="mainpage-post-bulb" />
        <div className="mainpage-post-button-text">나도 자바에서 팀원 모집하기!</div>
        <img src={mainpage_post_arrow} alt="오른쪽 화살표" className="mainpage-post-arrow" />
      </button>

      <div className="mainpage-subtitle-section">
        <div className="mainpage-subtitle-container">
          <div className="mainpage-subtitle">
            멘티 모집 중! 
            추천&nbsp;
            <strong>멘토</strong>들 소개
          </div>
          <img src={developer} alt="개발자아이콘" className="mainpage-subtitle-img" />
        </div>
        <div className="mainpage-dev-placeholder">
          <div className="mainpage-dev-scroll-cards">
            {developers.map((dev, index) => (
              <DeveloperCard key={index} {...dev} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
export default MainPage;