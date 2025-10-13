import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import api from '../../api/client';
import "./EditProfile.css";

// 이미지 import
import bannerBg from "./Profile_images/banner-bg.png";
import editIcon from "./Profile_images/edit-icon.png";
import closeBtn from "./Profile_images/close-btn.png";
import changeImg from "./Profile_images/change-img.png";
import profileDefault from "./Profile_images/profile-default.png";
import TimeTableModal from "../../components/TimeTableModal";

function EditProfile() {
  const navigate = useNavigate();
  const { user, updateUser, logout } = useAuth();

  // --- 로그 추가 1: AuthContext로부터 받은 원본 user 데이터 확인 ---
  console.log("EditProfile.jsx: AuthContext에서 받은 user", user);

  // 1. 텍스트 데이터를 관리하는 state
  const [formData, setFormData] = useState({
    name: "",
    field: "",
    university: "",
    portfolio: "",
    careers: {},
  });
  
  // 2. 파일 데이터를 별도로 관리하는 state (업로드할 실제 파일 객체)
  const [fileData, setFileData] = useState({
    avatar: null,
    banner: null,
    timetable: null,
  });

  // 3. 화면 미리보기를 위한 URL state
  const [previewUrls, setPreviewUrls] = useState({
    avatar_url: "",
    banner_url: "",
    timetable_url: "",
  });

  const [isEditingName, setIsEditingName] = useState(false);
  const [tempName, setTempName] = useState("");
  const [showModal, setShowModal] = useState(false);

  const avatarInputRef = useRef(null);
  const bannerInputRef = useRef(null);
  const nameInputRef = useRef(null);

  // 컴포넌트 마운트 시 user 정보로 state 초기화
  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || "",
        field: user.field || "",
        university: user.university || "",
        portfolio: user.portfolio || "",
        careers: user.careers || {},
      });
      setPreviewUrls({
        avatar_url: user.avatar_url || "",
        banner_url: user.banner_url || "",
        timetable_url: user.timetable_url || "",
      });
      // --- 로그 추가 2: user 데이터로 초기화된 formData와 previewUrls 확인 ---
      console.log("EditProfile.jsx: 초기화된 formData", {...formData, name: user.name});
      console.log("EditProfile.jsx: 초기화된 previewUrls", {...previewUrls, avatar_url: user.avatar_url, banner_url: user.banner_url, timetable_url: user.timetable_url});
    }
    else {
      alert("로그인이 필요한 서비스입니다.");
      navigate("/login", { replace: true });
    }
  }, [user, navigate]);

  // --- 입력 핸들러 ---
  const handleTextChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    if (files && files[0]) {
      const file = files[0];
      setFileData(prev => ({ ...prev, [name]: file }));
      setPreviewUrls(prev => ({ ...prev, [`${name}_url`]: URL.createObjectURL(file) }));
    }
  };

  // --- Careers 관련 핸들러 ---
  const sortedYears = Object.keys(formData.careers).sort((a, b) => Number(b) - Number(a));

  const updateCareers = (newCareers) => {
    setFormData(prev => ({ ...prev, careers: newCareers }));
  };
  
  const addYear = () => {
    const years = sortedYears.map(Number);
    const defaultYear = years.length ? String(Math.max(...years) + 1) : String(new Date().getFullYear());
    let y = Number(defaultYear);
    while (formData.careers[String(y)]) y++;
    const newCareers = { ...formData.careers, [String(y)]: [{id: Date.now(), description: ""}] };
    updateCareers(newCareers);
  };

  const addEntry = (year) => {
    const next = { ...formData.careers };
    next[year] = [...(next[year] || []), {id: Date.now(), description: ""}];
    updateCareers(next);
  };

  const updateEntry = (year, idx, value) => {
    const next = { ...formData.careers };
    next[year][idx] = { ...next[year][idx], description: value };
    updateCareers(next);
  };
  
  const removeEntry = (year, idx) => {
    const next = { ...formData.careers };
    next[year] = next[year].filter((_, i) => i !== idx);
    updateCareers(next);
  };

  const deleteYear = (year) => {
    if (window.confirm(`정말로 ${year}년의 모든 기록을 삭제하시겠습니까?`)) {
      const next = { ...formData.careers };
      delete next[year];
      updateCareers(next);
    }
  };

  // ✨ --- 연도 수정 핸들러 수정 --- ✨
  const renameYear = (oldYear, newYear) => {
    const y = String(newYear).trim();
    // 4자리 숫자인지, 기존 연도와 다른지, 이미 존재하는 연도가 아닌지 확인
    if (!/^\d{4}$/.test(y) || y === oldYear || formData.careers[y]) {
      // 유효하지 않으면 원래 값으로 되돌림 (사용자 경험을 위해 alert 추가 가능)
      alert("연도는 4자리 숫자여야 하며, 중복될 수 없습니다.");
      // input 값을 원래대로 되돌리기 위해 DOM을 직접 조작 (간단한 예시)
      const input = document.querySelector(`input[data-year='${oldYear}']`);
      if (input) input.value = oldYear;
      return;
    }

    const next = { ...formData.careers };
    // 기존 연도의 데이터를 새 연도로 옮기고, 기존 연도는 삭제
    next[y] = next[oldYear];
    delete next[oldYear];
    updateCareers(next);
  };

  const startNameEdit = () => {
    setTempName(formData.name);
    setIsEditingName(true);
    setTimeout(() => nameInputRef.current?.focus(), 0);
  };
  const commitName = () => {
    const nextName = tempName.trim();
    if (nextName) setFormData(prev => ({ ...prev, name: nextName }));
    setIsEditingName(false);
  };
  const onNameKeyDown = (e) => {
    if (e.key === "Enter") commitName();
    if (e.key === "Escape") setIsEditingName(false);
  };


  // --- 저장 핸들러 (API 명세에 맞춘 최종 버전) ---
  const handleSave = async () => {
    if (!user) return;

    const finalName = (isEditingName ? tempName : formData.name).trim();
    if (!finalName) {
      alert("이름은 필수입니다.");
      return;
    }
    
    const data = new FormData();
    data.append('name', finalName);
    data.append('field', formData.field);
    data.append('university', formData.university);
    data.append('portfolio', formData.portfolio);
    data.append('careers', JSON.stringify(formData.careers));

    if (fileData.avatar) data.append('avatar', fileData.avatar);
    if (fileData.banner) data.append('banner', fileData.banner);
    if (fileData.timetable) data.append('timetable', fileData.timetable);

    // --- 로그 추가 3: 서버로 보낼 FormData 데이터 확인 ---
    console.log("EditProfile.jsx: 서버로 전송할 FormData 객체입니다. 아래 내용을 펼쳐보세요.");
    for (let [key, value] of data.entries()) {
      // 파일 객체는 너무 길어질 수 있으므로 파일 이름만 출력
      if (value instanceof File) {
        console.log(`  ${key}:`, value.name);
      } else {
        console.log(`  ${key}:`, value);
      }
    }

    try {
      const response = await api.put(`/profile/${user.user_id}`, data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      updateUser(response.data.profile);
      alert("프로필이 저장되었습니다.");
      navigate(`/profile/${user.user_id}`, { replace: true });

    } catch (error) {
      console.error("프로필 저장 실패:", error);
      alert("프로필 저장 중 오류가 발생했습니다. 다시 시도해주세요.");
    }
  };

  // --- ✨ 회원 탈퇴 핸들러 수정 ✨ ---
  const handleDangerDelete = async () => {
    if (window.confirm("정말로 회원 탈퇴하시겠습니까?\n모든 데이터가 영구적으로 삭제되며, 복구할 수 없습니다.")) {
      if (!user) {
        alert("사용자 정보가 없어 탈퇴를 진행할 수 없습니다.");
        return;
      }
      try {
        // TODO: 백엔드 API 명세서에 맞는 회원 탈퇴 엔드포인트로 수정해야 합니다.
        await api.delete(`/users/me`); // 예시: 현재 로그인된 사용자 탈퇴
        
        alert("회원 탈퇴가 완료되었습니다. 이용해주셔서 감사합니다.");
        logout(); // AuthContext의 로그아웃 함수를 호출하여 프론트엔드 상태 정리
        navigate("/"); // 메인 페이지 또는 로그인 페이지로 이동

      } catch (error) {
        console.error("회원 탈퇴 실패:", error);
        alert("회원 탈퇴 중 오류가 발생했습니다.");
      }
    }
  };

  if (!user) return null;
  
  return (
    <div className="editprofile-page">
      <div
        className="editprofile-top-banner"
        style={{ backgroundImage: `url(${previewUrls.banner_url || bannerBg})` }}
        onClick={() => bannerInputRef.current?.click()}
      >
        <div className="glass-icon close" aria-label="닫기" onClick={(e) => { e.stopPropagation(); navigate(-1); }}>
          <img src={closeBtn} className="edit-closebtn"alt="닫기" />
        </div>
        <div className="glass-icon change" aria-label="배경 변경" onClick={(e) => { e.stopPropagation(); bannerInputRef.current?.click(); }}>
          <img src={changeImg} className="edit-changeImg" alt="배경 변경" />
        </div>
        <input name="banner" ref={bannerInputRef} type="file" accept="image/*" hidden onChange={handleFileChange} />
      </div>
      <div className="editprofile-img-wrapper">
        <div className="avatar-box" onClick={() => avatarInputRef.current?.click()}>
          <img src={previewUrls.avatar_url || profileDefault} alt="프로필" className="editprofile-img" />
          <div className="glass-icon avatar-change" aria-label="프로필 사진 변경">
            <img src={changeImg} className="edit-changeImg"alt="프로필 사진 변경" />
          </div>
          <input name="avatar" ref={avatarInputRef} type="file" accept="image/*" hidden onChange={handleFileChange} />
        </div>
        <button className="timetable-btn" onClick={() => setShowModal(true)}>
          시간표 보기
        </button>
      </div>
      <div className="editprofile-card">
        <div className="editprofile-name-row">
          <div className="editprofile-name">
            {!isEditingName ? (
              <>
                <div className="editprofile-name-text">{formData.name || "이름 없음"}</div>
                <img src={editIcon} className="editprofile-edit-btn" alt="이름 수정" onClick={startNameEdit} />
              </>
            ) : (
              <input
                ref={nameInputRef}
                className="editprofile-name-input"
                value={tempName}
                onChange={(e) => setTempName(e.target.value)}
                placeholder="이름을 입력하세요"
                maxLength={10}
                onKeyDown={onNameKeyDown}
                onBlur={commitName}
              />
            )}
          </div>
        </div>
        <div className="editprofile-tags">
          <span className="tag tag-field">{formData.field}</span>
          <span className="tag tag-univ">{formData.university}</span>
        </div>
        <div className="editprofile-form">
          <div className="form-row">
            <label className="form-label">포트폴리오</label>
            <div className="form-control">
              <input 
                name="portfolio"
                className="input" 
                type="url" 
                placeholder="링크를 입력하세요" 
                value={formData.portfolio} 
                onChange={handleTextChange} 
              />
              <button type="button" className="file-btn" onClick={() => formData.portfolio ? window.open(formData.portfolio, "_blank") : alert("포트폴리오 링크가 없습니다.")}>
                열기
              </button>
            </div>
          </div>
        </div>
        <div className="edit-profile-divider" />
        
        <div className="timeline-edit">
          {sortedYears.map((year) => (
            <div key={year} className="tl-year-block">
              <div className="tl-year-row">
                {/* 연도 수정 기능은 복잡성을 줄이기 위해 우선 제외 (필요 시 추가 가능) */}
                <input 
                  className="tl-year-input" 
                  defaultValue={year} 
                  maxLength={4}
                  // input 식별을 위한 data 속성 추가
                  data-year={year}
                  // onBlur: input에서 포커스가 벗어났을 때 함수 실행
                  onBlur={(e) => renameYear(year, e.target.value)} 
                />
                <img src={editIcon} alt="" className="tl-year-pencil" />
              </div>
              <ul className="tl-list">
                {(formData.careers[year] || []).map((item, idx) => (
                  <li key={item.id || idx} className="tl-item">
                    <span className="tl-dot" aria-hidden />
                    <input 
                      className="tl-input" 
                      placeholder="경험/수상/참여 기록을 입력하세요" 
                      value={item.description} 
                      onChange={(e) => updateEntry(year, idx, e.target.value)} 
                    />
                    <button type="button" className="tl-remove" onClick={() => removeEntry(year, idx)} aria-label="항목 삭제">삭제</button>
                  </li>
                ))}
                <li className="tl-add-row">
                  <button type="button" className="tl-add-link" onClick={() => addEntry(year)}>프로젝트 참여 경험 추가하기 +</button>
                </li>
              </ul>
              <div className="tl-year-actions">
                <button type="button" className="tl-year-delete" onClick={() => deleteYear(year)}>해당 연도 삭제하기</button>
              </div>
            </div>
          ))}
          <div className="tl-add-year-wrap">
            <button type="button" className="tl-add-year" onClick={addYear}>+ 연도 추가</button>
          </div>
        </div>

        <div className="editprofile-danger">
            <button className="danger-btn" onClick={handleDangerDelete}>회원 데이터 삭제하기</button>
        </div>
      </div>
      <div className="editprofile-footer-save">
        <button onClick={handleSave}>프로필 저장하기</button>
      </div>
      {showModal && <TimeTableModal onClose={() => setShowModal(false)} timetable_url={previewUrls.timetable_url} />}
    </div>
  );
}

export default EditProfile;