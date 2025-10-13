import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // 2. useNavigate 훅 임포트
import { useAuth } from '../../contexts/AuthContext'; // 1. useAuth 훅 임포트
import './EditInfoModal.css';
import api from '../../api/client';

const TRACKS = [
  // ... 트랙 데이터는 동일 ...
  { id: '프론트엔드', label: '프론트엔드', icon: 'frontend.png', iconClass: 'imgfrontend' },
  { id: '백엔드', label: '백엔드', icon: 'backend.png', iconClass: 'imgbackend' },
  { id: '기획', label: '기획', icon: 'plan.png', iconClass: 'imgplan' },
  { id: '디자인', label: '디자인', icon: 'design.png', iconClass: 'imgdesign' },
  { id: '데이터 분석', label: '데이터 분석', icon: 'dataanalysis.png', iconClass: 'imgdataanalysis' },
];

function EditInfoModal({ onClose }) {
  const navigate = useNavigate(); // useNavigate 훅 사용
  const { user, updateUser } = useAuth(); // 3. useAuth 훅 사용
  
  const [field, setField] = useState('');
  const [university, setUniversity] = useState('');

  useEffect(() => {
    // 4. 전역 user 상태에서 초기값 설정
    if (user) {
      setField(user.field || '');
      setUniversity(user.university || '');
    }
  }, [user]);

  // 변경점: 뒤로가기 핸들러 함수 추가
  const handleGoBack = () => {
    if (window.confirm("변경사항이 저장되지 않을 수 있습니다. 정말로 뒤로 가시겠습니까?")) {
      onClose(); // 모달 닫기
    }
    // 취소 시 아무것도 하지 않음
  };

  const handleSave = async () => {
    if (!field || !university) {
      alert('모든 필수 항목을 입력해주세요.');
      return;
    }
    try {
      const payload = { field, university };
      
      // 5. API 엔드포인트 확인 필요 (예: /profile/simple, /users/profile 등)
      await api.put('/mypage/users/me/basic', payload); 
      
      // 6. 전역 상태 업데이트
      updateUser(payload);

      // --- 📢 로그 추가: 업데이트 후 AuthContext의 user 객체 확인 ---
      console.log("EditInfoModal: updateUser 실행 후 MyPage로 전달될 user 데이터:", { ...user, ...payload });

      alert('정보가 성공적으로 변경되었습니다.');
      onClose(); // 모달 닫기
      // 변경점: 뒤로가기 대신 모달 닫기
    } catch (error) {
      console.error("프로필 업데이트 실패:", error);
      alert("정보 저장에 실패했습니다.");
    }
  };

  return (
    <div className="modal-overlay-sheet" onClick={handleGoBack}>
      <div className="modal-content-sheet" onClick={(e) => e.stopPropagation()}>
        {/* 헤더 */}
        <div className="edit-info-header">
          <img
            src="/arrow_back_ios.png"
            alt="뒤로가기"
            className="edit-info-back-button"
            onClick={handleGoBack} // 뒤로가기 핸들러 연결
          />
          <div className="edit-info-title">정보 수정</div>
        </div>
        
        <div className="edit-info-divider" />

        {/* 트랙 선택 */}
        <div className="edit-info-section">
          <div className="edit-info-label-group">
            <label className="edit-info-label">세부 트랙 선택*</label>
            <span className="edit-info-required-text">* 표시가 존재하는 항목은 필수 항목입니다.</span>
          </div>
          <div className="track-buttons-container">
            <div className="track-buttons-row">
              {TRACKS.slice(0, 2).map((track) => (
                <button key={track.id} type="button" className={`track-btn${field === track.label ? ' active' : ''}`} onClick={() => setField(track.label)}>
                  <img src={`/${track.icon}`} alt={track.label} className={track.iconClass} />
                  <span>{track.label}</span>
                </button>
              ))}
            </div>
            <div className="track-buttons-row">
              {TRACKS.slice(2).map((track) => (
                <button key={track.id} type="button" className={`track-btn${field === track.label ? ' active' : ''}`} onClick={() => setField(track.label)}>
                  <img src={`/${track.icon}`} alt={track.label} className={track.iconClass} />
                  <span>{track.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 학교 입력 */}
        <div className="edit-info-section">
          <label className="edit-info-label">재학생 등록*</label>
          <input
            type="text"
            className="edit-info-input"
            value={university}
            onChange={(e) => setUniversity(e.target.value)}
            placeholder="학교 이름을 입력하세요"
          />
          <p className="edit-info-description">
            ※띄어쓰기 없이 한글로 정확하게 입력 바랍니다. (예: 삼육대학교)
          </p>
        </div>
        
        <button className="edit-info-save-button" onClick={handleSave}>
          변경사항 저장하기
        </button>
      </div>
    </div>
  );
}

export default EditInfoModal;