// src/components/TimeTableModal.jsx

import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext"; // AuthContext 훅 import
import api from '../api/client'; // API 클라이언트 import
import "./TimeTableModal.css";
import closeIcon from "/close-btn.png";

// ✨ props로 timetable_url, onClose를 받도록 수정
function TimeTableModal({ timetable_url, onClose }) {
  const { user, updateUser } = useAuth();
  
  // ✨ 표시할 이미지 URL을 관리하는 state (초기값은 props로 받은 url)
  const [imageUrl, setImageUrl] = useState(timetable_url);
  const [isUploading, setIsUploading] = useState(false);

  // 파일 업로드 핸들러
  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !user) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append("timetable", file); // API 명세에 맞춰 'timetable' key 사용

    try {
      // 1. 서버에 이미지 업로드 API 호출
      const response = await api.post(
        `/profile/${user.user_id}/upload/timetable`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      
      const newTimetableUrl = response.data.timetable_url;
      
      // 2. 화면 및 전역 상태 업데이트
      setImageUrl(newTimetableUrl);
      updateUser({ timetable_url: newTimetableUrl });
      alert("시간표가 성공적으로 등록되었습니다.");

    } catch (error) {
      console.error("시간표 업로드 실패:", error);
      alert("시간표 업로드 중 오류가 발생했습니다.");
    } finally {
      setIsUploading(false);
    }
  };

  // 시간표 삭제 핸들러
  const handleRemove = async () => {
    if (!user || !window.confirm("정말로 시간표를 삭제하시겠습니까?")) return;

    try {
      // 1. 프로필 수정 API를 통해 timetable_url을 null로 설정
      //    (다른 프로필 정보는 그대로 유지)
      const payload = { ...user, timetable_url: null };
      const response = await api.put(`/profile/${user.user_id}`, payload);
      
      // 2. 화면 및 전역 상태 업데이트
      setImageUrl(null);
      updateUser({ timetable_url: null });
      alert("시간표가 삭제되었습니다.");

    } catch (error) {
      console.error("시간표 삭제 실패:", error);
      alert("시간표 삭제 중 오류가 발생했습니다.");
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="close-btn" onClick={onClose} aria-label="닫기">
          <img src={closeIcon} alt="닫기" className="close-icon-img" />
        </button>

        {imageUrl ? (
          <>
            <img src={imageUrl} alt="사용자 시간표" className="timetable-img" />
            <div className="timetable-actions">
              <label className={`reupload-btn ${isUploading ? "active" : ""}`}>
                {isUploading ? "업로드 중..." : "시간표 교체"}
                <input type="file" accept="image/*" onChange={handleUpload} hidden disabled={isUploading} />
              </label>
              <button className="remove-btn" onClick={handleRemove}>
                삭제
              </button>
            </div>
          </>
        ) : (
          <div className="upload-guide">
            <p>등록된 시간표가 없습니다.</p>
            <label className={`upload-btn ${isUploading ? "active" : ""}`}>
              {isUploading ? "업로드 중..." : "시간표 등록하기"}
              <input type="file" accept="image/*" onChange={handleUpload} hidden disabled={isUploading} />
            </label>
          </div>
        )}
      </div>
    </div>
  );
}

export default TimeTableModal;