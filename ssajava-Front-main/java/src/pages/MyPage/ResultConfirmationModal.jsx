// src/pages/MyPage/ResultConfirmationModal.jsx

import React, { useState } from 'react';
import api from '../../api/client';
import './ResultConfirmationModal.css';

function ResultConfirmationModal({ applicationId, applicant, onClose, onSuccess }) {
  const [link, setLink] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const sendResult = async (status) => {
    const payload = { status };
    if (status === '합격') {
      if (!link.startsWith('http')) {
        alert("합격 통보를 위한 외부 링크를 http:// 또는 https:// 형식으로 정확히 입력해주세요.");
        return;
      }
      payload.result_link = link;
    }

    setIsSubmitting(true);
    try {
      /*
        // --- API 호출 부분 주석 처리 ---
        await api.patch(`/applications/${applicationId}/status`, payload);
      */
      
      // API 호출 대신, 어떤 데이터를 보낼지 콘솔에 출력
      console.log("서버로 전송할 데이터:", payload);
      
      // 가짜로 1초 딜레이를 줘서 로딩 효과 확인
      await new Promise(resolve => setTimeout(resolve, 1000));

      alert(`'${applicant.name}'님에게 [${status}] 결과가 성공적으로 전송되었습니다.`);
      onSuccess(); // 성공 후 이전 페이지로 이동

    } catch (error) {
      alert("결과 전송 중 오류가 발생했습니다.");
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
// function ResultConfirmationModal({ applicationId, applicant, onClose, onSuccess }) {
//   const [link, setLink] = useState('');
//   const [isSubmitting, setIsSubmitting] = useState(false);

//   const sendResult = async (status) => {
//     const payload = { status };
//     if (status === '합격') {
//       if (!link.startsWith('http')) {
//         alert("합격 통보를 위한 외부 링크를 http:// 또는 https:// 형식으로 정확히 입력해주세요.");
//         return;
//       }
//       payload.result_link = link;
//     }

//     setIsSubmitting(true);
//     try {
//       await api.patch(`/applications/${applicationId}/status`, payload);
//       alert(`'${applicant.name}'님에게 [${status}] 결과가 성공적으로 전송되었습니다.`);
//       onSuccess();
//     } catch (error) {
//       alert("결과 전송 중 오류가 발생했습니다.");
//       console.error(error);
//     } finally {
//       setIsSubmitting(false);
//     }
//   };

  return (
    <div className="result-modal-overlay" onClick={onClose}>
      <div className="result-modal-content" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>×</button>
        <h3>결과 전송</h3>
        <div className="applicant-summary">
          <p><strong>{applicant.name}</strong></p>
          <p>{applicant.field} · {applicant.university}</p>
        </div>
        <div className="link-input-section">
          <label>외부 링크 (합격 시 필수)</label>
          <input 
            type="text" 
            placeholder="카카오톡 오픈채팅방 링크 등"
            value={link}
            onChange={e => setLink(e.target.value)}
          />
        </div>
        <div className="modal-action-buttons">
          <button className="reject-btn" onClick={() => sendResult('불합격')} disabled={isSubmitting}>
            지원 거절
          </button>
          <button className="accept-btn" onClick={() => sendResult('합격')} disabled={isSubmitting}>
            지원 수락
          </button>
        </div>
      </div>
    </div>
  );
}

export default ResultConfirmationModal;