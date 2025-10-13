import React from "react";
import { useNavigate } from "react-router-dom";
import "./Onboarding.css";

function Onboarding() {
  const navigate = useNavigate();

  const handleStart = () => {
    navigate("/login");
  };

  return (
    <div className="onboarding-container">
      <div className="onboarding-content">        
        <div className="onboarding-image">
          <img src="/onboarding-logo.png" className="onboarding-logo" alt="로고" />
        </div>
        <p className="onboarding-mid-text">
          팀원 모으고 싶은 사람?<br />
          <strong className="onboarding-point">자</strong><strong className="onboarding-point">바</strong>에서 기회를 <strong className="onboarding-point">잡</strong><strong className="onboarding-point">아</strong> 봐!
        </p>
        <button className="onboarding-button" onClick={handleStart}>
          시작하기
        </button>
      </div>
    </div>
  ); 
}

export default Onboarding;
