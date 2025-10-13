import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import './Signup2.css';

const TRACKS = [
  { id: '프론트엔드', label: '프론트엔드', icon: 'frontend.png', iconClass: 'imgfrontend' },
  { id: '백엔드', label: '백엔드', icon: 'backend.png', iconClass: 'imgbackend' },
  { id: '기획', label: '기획', icon: 'plan.png', iconClass: 'imgplan' },
  { id: '디자인', label: '디자인', icon: 'design.png', iconClass: 'imgdesign' },
  { id: '데이터 분석', label: '데이터 분석', icon: 'dataanalysis.png', iconClass: 'imgdataanalysis' },
];

function Signup2() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const { signupToken, email } = location.state || {};
  
  const [field, setField] = useState('');
  const [name, setName] = useState('');
  const [university, setUniversity] = useState('');
  const [portfolio, setPortfolio] = useState('');

  const isFormActive = field && name && university;

  useEffect(() => {
    if (!signupToken) {
      alert('잘못된 접근입니다. 로그인 페이지로 이동합니다.');
      navigate('/login');
    }
  }, [signupToken, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isFormActive) return;

    const payload = {
      signup_token: signupToken,
      email: email,
      name: name,
      field: field,
      university: university,
      portfolio: portfolio || null,
    };

    try {
      const signupResponse = await api.post('/auth/signup', payload);
      const { access_token } = signupResponse.data;

      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      const meResponse = await api.get('/auth/me');
      const userData = meResponse.data;
      
      login(userData, access_token);

      alert('회원가입이 성공적으로 완료되었습니다!');
      navigate('/home');
    } catch (error) {
      console.error('가입 요청 실패:', error);
      delete api.defaults.headers.common['Authorization'];
      if (error.response) {
        alert(error.response.data.message || '서버 처리 중 오류가 발생했습니다.');
      } else {
        alert('서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.');
      }
    }
  };

  return (
    <div className="signup2-wrapper">
      <div className="signup2-container">
        <form onSubmit={handleSubmit} className="signup2-form" autoComplete="off">
          <div className="form-section">
            <div className="section-title-group">
              <div className="section-title">세부 트랙 선택*</div>
              <div className="section-title2">* 표시가 존재하는 항목은 필수 항목입니다.</div>
            </div>
            <div className="track-buttons">
              <div className="track-buttons-header">
                {TRACKS.slice(0, 2).map((track) => (
                  <button key={track.id} type="button" className={`track-btn${field === track.label ? ' active' : ''}`} onClick={() => setField(track.label)}>
                    <img src={track.icon} className={track.iconClass} alt={`${track.label} 아이콘`} />
                    <span className="track-buttons-text">{track.label}</span>
                  </button>
                ))}
              </div>
              <div className="track-buttons-header2">
                {TRACKS.slice(2).map((track) => (
                  <button key={track.id} type="button" className={`track-btn${field === track.label ? ' active' : ''}`} onClick={() => setField(track.label)}>
                    <img src={track.icon} className={track.iconClass} alt={`${track.label} 아이콘`} />
                    <span className="track-buttons-text">{track.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="form-group">
            <label>이름*</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="이름을 입력하세요" maxLength={10} required />
          </div>

          <div className="form-group univ">
            <label>재학생 등록*</label>
            <input type="text" value={university} onChange={(e) => setUniversity(e.target.value)} placeholder="학교 이름을 입력하세요" maxLength={20} required />
          </div>

          <div className="form-group-discription">
            ※띄어쓰기 없이 한글로 정확하게 입력 바랍니다. (예: 삼육대학교)
          </div>

          <div className="form-group2">
            <label>포트폴리오 등록</label>
            <input type="text" value={portfolio} onChange={(e) => setPortfolio(e.target.value)} placeholder="포트폴리오 링크를 복사하세요" />
          </div>

          <button type="submit" className={`submit-btn${isFormActive ? ' active' : ''}`} disabled={!isFormActive}>
            가입하기
          </button>
        </form>
      </div>
    </div>
  );
}

export default Signup2;