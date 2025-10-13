
import React from "react";
import { useNavigate } from "react-router-dom";
import "./MyPageHeader.css";

function ApplicationHistoryHeader() {
  const navigate = useNavigate();

  const handleBack = () => {
    // 브라우저 히스토리에 따라 뒤로가거나 온보딩으로 이동
    if (window.history.length > 2) navigate(-1);
    else navigate('/');
  };

  return (
    <div className="mypage-header-container">
        <div className="mypage-header">
          <img
            src="/arrow_back_ios.png"
            alt="뒤로가기"
            className="back-icon"
            onClick={handleBack}
          />
          <div className="mypage-title">지원 내역</div>
        </div>
        {/* <div className="mypage-divider" /> */}
    </div>
  );
}
export default ApplicationHistoryHeader;