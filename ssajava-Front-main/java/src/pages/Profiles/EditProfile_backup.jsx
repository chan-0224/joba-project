import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import api from '../../api/client';
import "./EditProfile.css";

// 이미지 import
import bannerBg from "./Profile_images/banner-bg.png";
import editIcon from "./Profile_images/edit-icon.png";
import closeBtn from "./Profile_images/close-btn.png";
import changeImg from "./Profile_images/change-img.png";
import TimeTableModal from "../../components/TimeTableModal";

function EditProfile_backup() {
  const navigate = useNavigate();
  const { user, updateUser, logout } = useAuth();

  const [formData, setFormData] = useState({
    name: "",
    field: "",
    university: "",
    portfolio: "",
    banner_url: "",
    avatar_url: "",
    timetable_url: "",
    careers: {}, // timeline -> careers
  });
  
  const [isEditingName, setIsEditingName] = useState(false);
  const [tempName, setTempName] = useState("");
  const [showModal, setShowModal] = useState(false);

  const avatarInputRef = useRef(null);
  const bannerInputRef = useRef(null);
  const nameInputRef = useRef(null);

  useEffect(() => {
    if (!user) {
      alert("로그인이 필요한 서비스입니다.");
      navigate("/login", { replace: true });
    } else {
      setFormData({
        name: user.name || "",
        field: user.field || "",
        university: user.university || "",
        portfolio: user.portfolio || "",
        banner_url: user.banner_url || "",
        avatar_url: user.avatar_url || "",
        timetable_url: user.timetable_url || "",
        careers: user.careers || {},
      });
    }
  }, [user, navigate]);

  // --- 상태 업데이트 로직 ---
  const handleFormChange = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  const readAsDataURL = (file) =>
    new Promise((resolve, reject) => {
      const fr = new FileReader();
      fr.onload = () => resolve(fr.result);
      fr.onerror = reject;
      fr.readAsDataURL(file);
    });

  const onChangeBanner = async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const dataUrl = await readAsDataURL(f);
    handleFormChange('banner_url', dataUrl);
  };

  const onChangeAvatar = async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const dataUrl = await readAsDataURL(f);
    handleFormChange('avatar_url', dataUrl);
  };

  // --- Careers (타임라인) 관련 핸들러 ---
  const sortedYearsDesc = Object.keys(formData.careers).sort((a, b) => Number(b) - Number(a));

  const updateCareers = (newCareers) => {
    handleFormChange('careers', newCareers);
  };
  
  const addYear = () => {
    const years = sortedYearsDesc.map(Number);
    const defaultYear = years.length ? String(Math.max(...years) + 1) : String(new Date().getFullYear());
    let y = Number(defaultYear);
    while (formData.careers[String(y)]) y++;
    const newCareers = { ...formData.careers, [String(y)]: [""] };
    updateCareers(newCareers);
  };

  const renameYear = (oldYear, newYear) => {
    const y = String(newYear).trim();
    if (!/^\d{4}$/.test(y) || y === oldYear) return;
    const next = { ...formData.careers };
    if (next[y]) {
      next[y] = [...next[y], ...next[oldYear]];
    } else {
      next[y] = next[oldYear];
    }
    delete next[oldYear];
    updateCareers(next);
  };

  const deleteYear = (year) => {
    if (!window.confirm(`${year} 연도를 삭제할까요?`)) return;
    const next = { ...formData.careers };
    delete next[year];
    updateCareers(next);
  };

  const addEntry = (year) => {
    const next = { ...formData.careers };
    next[year] = [...(next[year] || []), ""];
    updateCareers(next);
  };

  const updateEntry = (year, idx, value) => {
    const next = { ...formData.careers };
    next[year][idx] = value;
    updateCareers(next);
  };

  const removeEntry = (year, idx) => {
    const next = { ...formData.careers };
    next[year] = next[year].filter((_, i) => i !== idx);
    updateCareers(next);
  };
  
  // --- 이름 수정 관련 핸들러 ---
  const startNameEdit = () => {
    setTempName(formData.name);
    setIsEditingName(true);
    setTimeout(() => nameInputRef.current?.focus(), 0);
  };

  const commitName = () => {
    const next = (tempName || "").trim();
    if (next) handleFormChange('name', next);
    setIsEditingName(false);
  };
  
  const cancelName = () => setIsEditingName(false);

  const onNameKeyDown = (e) => {
    if (e.key === "Enter") commitName();
    if (e.key === "Escape") cancelName();
  };

  // --- 저장 및 탈퇴 핸들러 ---
  const handleSave = async () => {
    if (!user) return; // user가 없으면 저장 방지

    const finalName = (isEditingName ? tempName : formData.name).trim();
    if (!finalName) {
      alert("이름은 필수입니다.");
      return;
    }
    const payload = { ...formData, name: finalName };

    try {
      await api.put(`/profile/${user.user_id}`, payload);
      updateUser(payload);
      alert("프로필이 저장되었습니다.");
      navigate(`/profile/${user.user_id}`, { replace: true });
    } catch (error) {
      console.error("프로필 저장 실패:", error);
      alert("프로필 저장 중 오류가 발생했습니다. 다시 시도해주세요.");
    }
  };

  const handleDangerDelete = async () => {
    if (window.confirm("정말로 회원 탈퇴하시겠습니까? 모든 데이터가 영구적으로 삭제됩니다.")) {
      try {
        await api.delete('/users/me'); // 백엔드 회원 탈퇴 API (예시)
        alert("회원 탈퇴 처리되었습니다.");
        logout();
        navigate("/login", { replace: true });
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
        style={{ backgroundImage: `url(${formData.banner_url || bannerBg})` }}
        onClick={() => bannerInputRef.current?.click()}
      >
        <div className="glass-icon close" aria-label="닫기" onClick={(e) => { e.stopPropagation(); navigate(-1); }}>
          <img src={closeBtn} className="edit-closebtn" alt="닫기" />
        </div>
        <div className="glass-icon change" aria-label="배경 변경" onClick={(e) => { e.stopPropagation(); bannerInputRef.current?.click(); }}>
          <img src={changeImg} className="edit-changeImg" alt="배경 변경" />
        </div>
        <input ref={bannerInputRef} type="file" accept="image/*" hidden onChange={onChangeBanner} />
      </div>
      <div className="editprofile-img-wrapper">
        <div className="avatar-box" onClick={() => avatarInputRef.current?.click()}>
          <img src={formData.avatar_url || "/mainlogo.png"} alt="프로필" className="editprofile-img" />
          <div className="glass-icon avatar-change" aria-label="프로필 사진 변경">
            <img src={changeImg} className="edit-changeImg" alt="프로필 사진 변경" />
          </div>
          <input ref={avatarInputRef} type="file" accept="image/*" hidden onChange={onChangeAvatar} />
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
                <div className="editprofile-name-text">{formData.name || "홍길동"}</div>
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
          {formData.field && <span className="tag tag-field">{formData.field}</span>}
          {formData.university && <span className="tag tag-univ">{formData.university}</span>}
        </div>
        <div className="editprofile-form">
          <div className="form-row">
            <label className="form-label">포트폴리오</label>
            <div className="form-control">
              <input 
                className="input" 
                type="url" 
                placeholder="링크를 입력하세요" 
                value={formData.portfolio} 
                onChange={(e) => handleFormChange('portfolio', e.target.value)} 
              />
              <button type="button" className="file-btn" onClick={() => formData.portfolio ? window.open(formData.portfolio, "_blank") : alert("포트폴리오 링크가 없습니다.")}>
                열기
              </button>
            </div>
          </div>
        </div>
        <div className="edit-profile-divider" />
        <div className="timeline-edit">
          {sortedYearsDesc.map((year) => (
            <div key={year} className="tl-year-block">
              <div className="tl-year-row">
                <input className="tl-year-input" defaultValue={year} maxLength={4} onBlur={(e) => renameYear(year, e.target.value)} />
                <img src={editIcon} alt="" className="tl-year-pencil" />
              </div>
              <ul className="tl-list">
                {(formData.careers[year] || []).map((item, idx) => (
                  <li key={idx} className="tl-item">
                    <span className="tl-dot" aria-hidden />
                    <input className="tl-input" placeholder="경험/수상/참여 기록을 입력하세요" value={item} onChange={(e) => updateEntry(year, idx, e.target.value)} />
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
      {showModal && <TimeTableModal onClose={() => setShowModal(false)} timetable_url={formData.timetable_url} />}
    </div>
  );
}

export default EditProfile_backup;