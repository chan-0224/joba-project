// src/components/ImageViewerModal.jsx

import React from 'react';
import './ImageViewerModal.css';

function ImageViewerModal({ imageUrl, alt, onClose }) {
  if (!imageUrl) {
    return null;
  }

  return (
    <div className="image-modal-overlay" onClick={onClose}>
      <div className="image-modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="image-modal-close-btn" onClick={onClose}>×</button>
        <img src={imageUrl} alt={alt} className="image-modal-img" />
      </div>
    </div>
  );
}

export default ImageViewerModal;