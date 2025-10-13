
import React from "react";
import { useNavigate } from "react-router-dom";
import "./MyPageHeader.css";

function RecruitmentHistoryHeader() {
  const navigate = useNavigate();

  const handleBack = () => {
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
          <div className="mypage-title">모집 내역</div>
        </div>
        {/* <div className="mypage-divider" /> */}
    </div>
  );
}
export default RecruitmentHistoryHeader;