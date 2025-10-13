import React, { useState } from 'react';
import './Signup.css';
import { useNavigate } from 'react-router-dom';

function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    id: '',
    password: '',
    confirm: '',
    name: '',
    email: '',
  });

  const [isIdChecked, setIsIdChecked] = useState(false); // 중복확인 완료 여부
  //근데 왜 중복확인 안되냐;; 짱나게 ;;
  const [isIdValid, setIsIdValid] = useState(false);     // 아이디 유효 여부
  
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleCheck = () => {
    const { id } = form;
    if (!id.trim()) {
      alert('아이디를 입력해주세요');
      setIsIdChecked(false);
      return;
    }
    // TODO: 실제 API 콜 대신 예시 로직!!!!!!!!
    if (id === 'testuser') {
      alert('이미 사용 중인 아이디입니다.');
      setIsIdValid(false);
    } else {
      alert('사용 가능한 아이디입니다.');
      setIsIdValid(true);
    }
    setIsIdChecked(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!isIdChecked) {
      alert("아이디 중복확인을 해주세요.");
      return;
    }

    if (!isIdValid) {
      alert("이미 사용 중인 아이디입니다. 다른 아이디를 입력하세요.");
      return;
    }

    if (form.password !== form.confirm) {
      alert('비밀번호가 일치하지 않습니다.');
      return;
    }

    localStorage.setItem('signupBasic', JSON.stringify(form));
    navigate('/signup2');
  };

  return (
    <div className="signup-container">
      <form className="signup-form" onSubmit={handleSubmit}>
        <div className="signup-field">
          <label className="signup-label">아이디</label>
          <div className="signup-id">
            <input
              name="id"
              placeholder="아이디를 입력하세요 (6~20자)"
              className="signup-input-id"
              value={form.id}
              onChange={handleChange}
              required
            />
            <button
              type="button"
              className="signup-check-button"
              onClick={handleCheck}
            >
              중복확인
            </button>
          </div>
        </div>

        <div className="signup-field">
          <label className="signup-label">비밀번호</label>
          <input
            name="password"
            type="password"
            placeholder="비밀번호를 입력하세요 (문자, 숫자, 특수문자 포함 8~20자)"
            className="signup-input"
            value={form.password}
            onChange={handleChange}
            required
          />
        </div>

        <div className="signup-field">
          <label className="signup-label">비밀번호 확인</label>
          <input
            name="confirm"
            type="password"
            placeholder="비밀번호를 다시 입력하세요"
            className="signup-input"
            value={form.confirm}
            onChange={handleChange}
            required
          />
        </div>

        <div className="signup-field">
          <label className="signup-label">이름</label>
          <input
            name="name"
            type="text"
            placeholder="이름을 입력하세요"
            className="signup-input"
            value={form.name}
            onChange={handleChange}
            required
          />
        </div>

        <div className="signup-field">
          <label className="signup-label">이메일</label>
          <input
            name="email"
            type="email"
            placeholder="이메일을 입력하세요"
            className="signup-input"
            value={form.email}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit" className="signup-button">프로필 정보 입력하기</button>
      </form>
    </div>
  );
};

export default Signup;
