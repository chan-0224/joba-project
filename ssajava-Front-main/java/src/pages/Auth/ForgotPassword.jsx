import React, { useState } from 'react';
import './ForgotPassword.css';
import { useNavigate } from 'react-router-dom';

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: 실제 이메일 처리 로직 연동
    alert(`${email} 주소로 임시 비밀번호를 전송했습니다.`);
    navigate('/login');
  };

  return (
    <div className="forgot-container">
      <h1 className="forgot-title">비밀번호 찾기</h1>
      <p className="forgot-description">
        가입하신 이메일 주소를 입력해주세요. <br />
        임시 비밀번호를 보내드립니다.
      </p>
      <form className="forgot-form" onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="이메일 주소"
          className="forgot-input"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <button type="submit" className="forgot-button">전송하기</button>
      </form>
    </div>
  );
};

export default ForgotPassword;
