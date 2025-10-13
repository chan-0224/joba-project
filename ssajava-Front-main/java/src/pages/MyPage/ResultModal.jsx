import React from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/client';

import closeIcon from "/close-btn.png";
import './ResultModal.css';

// 이미지 import
import congratsIcon from './modal_icons/congrats.png';
import rejectedIcon from './modal_icons/rejected.png';
import pendingIcon from './modal_icons/pending.png';
import cancelledIcon from './modal_icons/cancelled.png';

function ResultModal({ application, onClose, onCancelSuccess }) {
  const navigate = useNavigate();

  const handleCancelApplication = async () => {
    if (window.confirm("정말로 지원을 취소하시겠습니까?")) {
      try {
        // TODO: 아래 API 주석을 풀고 실제 엔드포인트로 교체하세요.
        // await api.delete(`/v1/applications/${application.application_id}`);
        
        alert("지원을 취소했습니다.");
        onCancelSuccess(application.application_id);

      } catch (error) {
        console.error("지원 취소에 실패했습니다.", error);
        alert("지원 취소 중 오류가 발생했습니다.");
      }
    }
  };

  const getModalContent = () => {
    switch (application.status) {
      case '합격':
        return {
          icon: congratsIcon,
          iconSize: { width: 121, height: 121 }, // 아이콘 크기 지정
          title: "합격 축하드립니다!",
          text: "원활한 공모전 활동을 위해 준비된 링크로 와주세요.",
          buttons: [
            <a href={application.result_link} key="link" target="_blank" rel="noopener noreferrer" className="result-modal-btn yellow">
              이동하기
            </a>
          ]
        };
      case '불합격':
        return {
          icon: rejectedIcon,
          iconSize: { width: 139, height: 139 }, // 아이콘 크기 지정
          title: "아쉽게도 해당 공고에 거절되었어요.",
          text: "다른 곳에 더 참여해보세요!",
          buttons: [
            <button key="find" className="result-modal-btn pink" onClick={() => { navigate('/home'); onClose(); }}>
              공고 찾으러 가기
            </button>
          ]
        };
      case '취소됨':
        return {
          icon: cancelledIcon,
          iconSize: { width: 146, height: 146 }, // 아이콘 크기 지정
          title: "지원을 취소했습니다.",
          text: "",
          buttons: []
        };
      case '제출됨':
      default:
        return {
          icon: pendingIcon,
          iconSize: { width: 146, height: 146 }, // 아이콘 크기 지정
          title: "해당 공고는 아직 결과가 나오지 않았어요.",
          text: "",
          buttons: [
            <button key="cancel" className="result-modal-btn gray" onClick={handleCancelApplication}>
              지원 취소하기
            </button>,
            <button key="find" className="result-modal-btn pink" onClick={() => { navigate('/home'); onClose(); }}>
              공고 찾으러 가기
            </button>
          ]
        };
    }
  };

  const content = getModalContent();

  return (
    <div className="result-modal-overlay" onClick={onClose}>
      <div className="result-modal-content" onClick={(e) => e.stopPropagation()}>
        <div>
            <img src={closeIcon} alt="닫기" className="result-modal-close-btn" onClick={onClose} aria-label="닫기"/>
        </div>
        {/* 변경점: 내부 요소들을 감싸는 div 추가 */}
        <div className="result-modal-inner-content">
          <img 
            src={content.icon} 
            alt={content.title} 
            className="result-modal-icon"
            // 변경점: 인라인 스타일로 아이콘 크기 동적 적용
            style={{ width: `${content.iconSize.width}px`, height: `${content.iconSize.height}px` }}
          />
          <h2 className="result-modal-title">{content.title}</h2>
          {content.text && <p className="result-modal-text">{content.text}</p>}
          <div className="result-modal-buttons">{content.buttons}</div>
        </div>
      </div>
    </div>
  );
}

export default ResultModal;