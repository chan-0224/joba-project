import React from 'react';
import './DeveloperCard.css';

function DeveloperCard({ name, field, university, avatar, background }) {
  return (
    <div className="dev-card">
      {/* 배경 이미지 */}
      <div
        className="dev-background"
        style={{ backgroundImage: `url(${background})` }} // 오직 배경이미지만
      />

      {/* 하단 카드 (흰 배경) */}
      <div className="dev-info-card">
        <img src={avatar} alt={`${name} 프로필`} className="dev-avatar" />
        <div className="dev-name">{name}</div>
        <div className="dev-tags">
          <span className="dev-tag dev-field">{field}</span>
          <span className="dev-tag dev-univ">{university}</span>
        </div>
      </div>
    </div>
  );
}

export default DeveloperCard;
