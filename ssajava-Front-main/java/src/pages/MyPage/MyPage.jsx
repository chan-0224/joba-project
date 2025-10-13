import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './MyPage.css';
//import { logout } from '../../api/auth';

import EditInfoModal from './EditInfoModal';
import { useAuth } from '../../contexts/AuthContext';

import api from '../../api/client';

// 이미지 import
import profileDefault from '../Profiles/Profile_images/profile-default.png';
import arrowRight from '../Profiles/Profile_images/arrow_right.png';

import settingIcon from './images/setting.png';

// 카드 아이콘 이미지
import applyHistoryIcon from './images/apply-history.png';
import recruitHistoryIcon from './images/recruit-history.png';

// 설정 아이콘 이미지
import serviceNoticeIcon from './images/service-notice.png';
import versionControlIcon from './images/version-control.png';
import logoutIcon from './images/logout.png';
import withdrawIcon from './images/withdraw.png';


function MyPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [isModalOpen, setIsModalOpen] = useState(false);

  // --- ✨ 모달 상태에 따라 body 클래스를 제어하는 useEffect 추가 ---
  useEffect(() => {
    // isModalOpen이 true이면 body에 'modal-open' 클래스 추가
    if (isModalOpen) {
      document.body.classList.add('modal-open');
    } else {
      document.body.classList.remove('modal-open');
    }

    // 컴포넌트가 사라질 때(unmount)를 대비해 정리(cleanup) 함수를 반환합니다.
    // 이렇게 하면 다른 페이지로 이동했을 때 클래스가 남아있는 문제를 방지할 수 있습니다.
    return () => {
      document.body.classList.remove('modal-open');
    };
  }, [isModalOpen]); // isModalOpen 상태가 변경될 때마다 이 함수가 실행됩니다.
  // -----------------------------------------------------------

  const handleLogout = () => {
    if (window.confirm('정말 로그아웃 하시겠어요?')) {
      logout();
      alert('로그아웃 되었습니다.');
      navigate('/login');
    }
  };
  
  const handleWithdraw = () => {
    if (window.confirm('정말로 계정을 탈퇴하시겠습니까?\n모든 데이터가 영구적으로 삭제됩니다.')) {
      alert('회원 탈퇴 기능은 준비 중입니다.');
    }
  };
  
  // user가 없을 경우를 대비해 optional chaining(?.) 사용
  const profileImgSrc = user?.avatar_url || profileDefault;
  const userFieldInfo = [user?.field, user?.university].filter(Boolean).join(' · ');

  // user 정보가 아직 로딩 중이거나 없을 경우를 대비
  if (!user) {
    return <div>사용자 정보를 불러오는 중...</div>; 
  }

  return (
    <>
    <div className="mypage-container-new">
      {/* 사용자 프로필 섹션 */}
      <div className="mypage-profile-section">
        <img src={profileImgSrc} alt="Profile" className="mypage-avatar-new" />
        <div className="mypage-user-details">
          <div className="mypage-username-new">
            <div className="mypage-username-context">{user.name || '사용자'}</div>
            <img src={settingIcon} alt="설정" className="mypage-setting-icon" 
              // 변경점: 클릭 시 페이지 이동 대신 모달을 열도록 변경
                onClick={(e) => {
                  e.stopPropagation(); // 부모 요소(프로필 섹션)의 클릭 이벤트 방지
                  setIsModalOpen(true);
            }}/>
          </div>
          <div className="mypage-user-field">{userFieldInfo}</div>
        </div>
      </div>

      {/* 메인 카드 메뉴 */}
      <div className="card-header">나의 공고</div>
      <div className="mypage-main-cards">
        <div className="mypage-card" onClick={() => navigate('/application-history')} /*onClick={() => alert('지원 내역 페이지는 준비 중입니다.')}*/>
          <div className="card-text">
            <div className="card-title">지원 내역</div>
          </div>
          <img src={applyHistoryIcon} alt="지원 내역" className="card-icon" />
        </div>
        <div className="mypage-card" onClick={() => navigate('/recruitment-history')} /*onClick={() => alert('모집 내역 페이지는 준비 중입니다.')}*/>
          <div className="card-text">
            <div className="card-title">모집 내역</div>
          </div>
          <img src={recruitHistoryIcon} alt="모집 내역" className="card-icon" />
        </div>
      </div>

      {/* 설정 및 정보 메뉴 */}
      <div className="list-header">설정</div>
      <div className="mypage-settings-list">
        <div className="list-item" 
          /*onClick={() => alert('서비스 공지사항 페이지는 준비 중입니다.')}*/
          onClick={() => navigate('/announcements')}>
          <img src={serviceNoticeIcon} alt="서비스 공지사항" className="list-item-icon" />
          <span className="list-item-text">서비스 공지사항</span>
          <img src={arrowRight} alt=">" className="list-arrow-icon" />
        </div>
        
        <div className="list-item">
          <img src={versionControlIcon} alt="버전 정보" className="list-item-icon" />
          <span className="list-item-text">
            버전 정보
            <span className="version-info">1.0.0</span>
          </span>
          <img src={arrowRight} alt=">" className="list-arrow-icon" />
        </div>
        
        <div className="list-item" onClick={handleLogout}>
          <img src={logoutIcon} alt="로그아웃" className="list-item-icon" />
          <span className="list-item-text">로그아웃</span>
          <img src={arrowRight} alt=">" className="list-arrow-icon" />
        </div>
        <div className="list-item" onClick={handleWithdraw}>
          <img src={withdrawIcon} alt="회원 탈퇴" className="list-item-icon" />
          <span className="list-item-text withdraw">회원 탈퇴</span>
          <img src={arrowRight} alt=">" className="list-arrow-icon" />
        </div>
      </div>
    </div>
    {/* 변경점: isModalOpen이 true일 때만 EditInfoModal을 렌더링하고, 닫기 함수를 전달합니다. */}
      {isModalOpen && <EditInfoModal onClose={() => setIsModalOpen(false)} />}
    </>
  );
}

export default MyPage;