// src/pages/MyPage/RecruitmentHistoryPage.jsx

import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/client';
import './RecruitmentHistoryPage.css';
import pinkfire from '../Home/Home_images/pinkfire.png';

import RecruitmentHistoryHeader from '../../components/RecruitmentHistoryHeader';

// --- 트랙별 아이콘 매핑 객체 ---
const TRACK_ICONS = {
  '프론트엔드': '/frontend.png',
  '백엔드': '/backend.png',
  '디자인': '/design.png',
  '기획': '/plan.png',
  '데이터 분석': '/dataanalysis.png',
};

// --- 임시 데이터 (상세 정보 추가) ---
const MOCK_POSTS = [
  { 
    id: 1, 
    title: '임베디드 소프트웨어 경진대회 프론트엔드 모집', 
    description: '디자인 파트와 개발 파트를 동시에 구인 중입니다.',
    image_url: '/Home/Home_images/job3.jpg',
    recruitment_status: '모집중', 
    recruitment_field: '프론트엔드',
    application_count: 4,
    recruited_count: 3,
  },
  { 
    id: 2, 
    title: 'SW 경진대회 UIUX 파트 모집', 
    description: '2025년 SW경진대회 함께할 UIUX 디자이너 모집합니다.',
    image_url: '/Home/Home_images/job1.jpg',
    recruitment_status: '모집중', 
    recruitment_field: '디자인',
    application_count: 17,
    recruited_count: 2,
  },
  { 
    id: 3, 
    title: 'KOICA 활용 챌린지 함께할 디자이너 모집',
    description: '프로젝트 경험 없어도 열정 하나만 있다면 OK',
    image_url: '/Home/Home_images/job2.jpg',
    recruitment_status: '모집종료', 
    recruitment_field: '디자인',
    application_count: 31,
    recruited_count: 2,
  },
];

function RecruitmentHistoryPage() {
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openSections, setOpenSections] = useState({ recruiting: true, ended: true });

  useEffect(() => {
    const fetchMyPosts = async () => {
      try {
        setLoading(true);
        /* // --- API 호출 부분 주석 처리 ---
          const response = await api.get('/posts/me');
          setPosts(response.data);
        */
        // --- Mock Data 사용 ---
        setPosts(MOCK_POSTS);

      } catch (error) {
        console.error("내 모집 공고를 불러오는 데 실패했습니다.", error);
      } finally {
        setLoading(false);
      }
    };
    fetchMyPosts();
  }, []);

  const groupedPosts = useMemo(() => {
    const recruiting = { count: 0, tracks: {} };
    const ended = { count: 0, tracks: {} };

    posts.forEach(post => {
      // API 명세서의 recruitment_status 필드 사용
      if (post.recruitment_status === '모집중') {
        recruiting.count++;
        // API 명세서의 recruitment_field 필드 사용
        if (!recruiting.tracks[post.recruitment_field]) recruiting.tracks[post.recruitment_field] = [];
        recruiting.tracks[post.recruitment_field].push(post);
      } else {
        ended.count++;
        if (!ended.tracks[post.recruitment_field]) ended.tracks[post.recruitment_field] = [];
        ended.tracks[post.recruitment_field].push(post);
      }
    });
    return { recruiting, ended };
  }, [posts]);

  const toggleSection = (section) => {
    setOpenSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const getPostCount = (groupedData) => {
    return Object.values(groupedData).reduce((acc, trackPosts) => acc + trackPosts.length, 0);
  };
  
  if (loading) {
    return <div>내 모집 공고를 불러오는 중...</div>
  }

  return (
    <>
      <RecruitmentHistoryHeader />
    <div className="recruitment-history-page">      
      <section className="recruitment-section">
        <div className="section-header" onClick={() => toggleSection('recruiting')}>
          <h2>모집 중인 공고 <span className="recruit-count">{groupedPosts.recruiting.count}</span></h2>
          <span className={`toggle-text ${openSections.recruiting ? 'open' : ''}`}>
            {openSections.recruiting ? '접기' : '펼치기'}
          </span>
        </div>
        {openSections.recruiting && (
          <div className="post-group-wrapper">
            {Object.entries(groupedPosts.recruiting.tracks).map(([track, trackPosts]) => (
              <PostGroup key={track} track={track} posts={trackPosts} />
            ))}
          </div>
        )}
      </section>

      <section className="recruitment-section">
        <div className="section-header" onClick={() => toggleSection('ended')}>
          <h2>모집 종료된 공고 <span className="recruit-count">{groupedPosts.ended.count}</span></h2>
           <span className={`toggle-text ${openSections.ended ? 'open' : ''}`}>
            {openSections.ended ? '접기' : '펼치기'}
          </span>
        </div>
        {openSections.ended && (
          <div className="post-group-wrapper">
            {Object.entries(groupedPosts.ended.tracks).map(([track, trackPosts]) => (
              <PostGroup key={track} track={track} posts={trackPosts} />
            ))}
          </div>
        )}
      </section>
    </div>
    </>
  );
}

const PostGroup = ({ track, posts }) => {
  const navigate = useNavigate();
  return (
    <div className="post-group">
      <h3 className="track-title">
        <img src={TRACK_ICONS[track] || '/frontend.png'} alt={track} className="track-icon" />
        {track}
      </h3>
      <div className="post-list">
        {posts.map(post => (
          <div key={post.id} className="recruitment-item" onClick={() => navigate(`/posts/${post.id}/applications`)}>
            <img src={post.image_url} alt={post.title} className="post-image" />
            <div className="post-info">
              <h4 className="post-title">{post.title}</h4>
              <p className="post-description">{post.description}</p>
              <div className="post-meta">
                <span className="meta-applicants">
                  <img src={pinkfire} alt="지원자" className="meta-icon" />
                  {post.application_count}명 지원 중
                </span>
                <span className="meta-headcount">
                  {post.recruited_count}명 모집
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecruitmentHistoryPage;