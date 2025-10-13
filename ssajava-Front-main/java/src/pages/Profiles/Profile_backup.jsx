import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import api from '../../api/client';
import "./Profile.css";

// 이미지 import (생략)
import bannerBg from "./Profile_images/banner-bg.png";
import profileDefault from "./Profile_images/profile-default.png";
import editIcon from "./Profile_images/edit-icon.png";
import TimeTableModal from "../../components/TimeTableModal";
import projectIcon from "./Profile_images/recent-title-icon.png";
import arrowRight from "./Profile_images/arrow_right.png";

function Profile_backup() {
  const navigate = useNavigate();
  const { userId } = useParams();
  const { user: loggedInUser, updateUser } = useAuth();

  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    const targetUserId = userId || loggedInUser?.user_id;

    if (!targetUserId) {
      setLoading(false);
      if (!loggedInUser) {
        navigate('/login');
      }
      return;
    }

    const fetchUserProfile = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await api.get(`/profile/${targetUserId}`); // v1은 client.js에 설정됨
        setProfileData(response.data);

        if (loggedInUser?.user_id === targetUserId) {
          updateUser(response.data);
        }
      } catch (err) {
        console.error("프로필 로딩 실패:", err);
        setError("프로필을 불러올 수 없습니다.");
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, [userId, loggedInUser?.user_id, updateUser, navigate]);

  if (loading) {
    return <div>프로필을 불러오는 중...</div>;
  }

  if (error || !profileData) {
    return <div>{error || "프로필 정보를 찾을 수 없습니다."}</div>;
  }

  const {
    name,
    field,
    university,
    portfolio,
    banner_url,
    avatar_url,
    timetable_url,
    careers = {},
    recent_projects = []
  } = profileData;

  const isOwnProfile = loggedInUser?.user_id === profileData.user_id;

  const sortedYears = useMemo(
    () => Object.keys(careers).sort((a, b) => Number(b) - Number(a)),
    [careers]
  );

  const goEdit = () => navigate("/edit-profile");
  
  return (
    <>
      <div className="profile-container">
        <div className="profile-top-banner">
          <img src={banner_url || bannerBg} alt="배경" className="profile-banner-img" />
        </div>
        <div className="profile-img-wrapper">
          <img src={avatar_url || profileDefault} alt="프로필" className="profile-img" />
          <button className="timetable-btn" onClick={() => setShowModal(true)}>
            시간표 보기
          </button>
        </div>
        <div className="profile-info-wrapper">
          <div className="profile-name">{name || "사용자"}</div>
          {isOwnProfile && (
            <img src={editIcon} className="profile-edit-btn" alt="프로필 수정" onClick={goEdit}/>
          )}
        </div>
        <div className="profile-tags">
          {field && <span className="profile-tag field">{field}</span>}
          {university && <span className="profile-tag univ">{university}</span>}
        </div>
        <div className="portfolio-section">
          <p className="portfolio-label">포트폴리오</p>
          <input type="text" className="portfolio-input" value={portfolio || ""} disabled placeholder="https://notefolio.net/yyyy"/>
        </div>
        <div className="profile-divider" />
        
        <div className="timeline-section">
          {sortedYears.map((year) => (
            <React.Fragment key={year}>
              <div className="year-title">{year}</div>
              <ul className="timeline-list">
                {(careers[year] || []).map((item, index) => (
                  <li key={item?.id || index} className="timeline-item">
                    <span className="timeline-dot" aria-hidden="true" />
                    {typeof item === 'object' ? item.description : item}
                  </li>
                ))}
              </ul>
            </React.Fragment>
          ))}
        </div>
        
        <div className="recent-projects">
          <div className="recent-title-wrapper">
            <div className="recent-title">자바에서 최근 함께한 프로젝트</div>
            <img src={projectIcon} alt="프로젝트아이콘" className="recent-title-img" />
          </div>
          <div className="project-cards">
            {recent_projects.length > 0 ? (
              recent_projects.map((proj, index) => (
                <div key={proj?.id || index} className="project-card" style={{ backgroundImage: `url(${proj?.image_url || ''})` }}>
                  <div className="project-card-text">{proj?.title}</div>
                  <img src={arrowRight} alt="화살표" className="project-card-arrow" />
                </div>
              ))
            ) : (
              <p>참여한 프로젝트가 없습니다.</p>
            )}
          </div>
        </div>
      </div>
      <div id="modal-root"></div>
      {showModal && <TimeTableModal onClose={() => setShowModal(false)} timetable_url={timetable_url} />}
    </>
  );
}

export default Profile_backup;