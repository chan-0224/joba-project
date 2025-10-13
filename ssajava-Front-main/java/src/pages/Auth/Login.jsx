// src/pages/Auth/Login.jsx
import React, { useState } from "react";
import "./Login.css";

const BASE = import.meta.env.VITE_API_BASE_URL || "https://joba-project.onrender.com";
const API_PREFIX = import.meta.env.VITE_API_PREFIX || "/v1";
const AUTH_LOGIN_PATH = `${API_PREFIX}/auth/login`;

// 👉 핑 경로를 /ping(루트)로 고정. 필요하면 .env에 VITE_PING_PATH=/ping 지정 가능.
const PING_PATH = import.meta.env.VITE_PING_PATH || "/ping";

// Render 콜드스타트 웜업: 502/503이면 재시도, 그 외(200/401/403/404 등)는 “깨어남”으로 간주
async function warmBackend(base, pingPath = "/ping", retries = 6) {
  const url = `${base}${pingPath}`;
  let delay = 500;
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(url, { method: "GET", cache: "no-store" });
      if (res.status !== 502 && res.status !== 503) return true;
    } catch (_) {}
    await new Promise((r) => setTimeout(r, delay));
    delay = Math.min(Math.round(delay * 1.8), 4000);
  }
  return false;
}

export default function Login() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  const startSocial = async (provider) => {
    if (loading) return;
    setLoading(true);
    setStatus("서버 깨우는 중…");

    // ✅ /ping(루트)으로 웜업
    await warmBackend(BASE, PING_PATH);

    setStatus("로그인 페이지로 이동 중…");
    const front = `${window.location.origin}/oauth/callback/${provider}`;
    window.location.href = `${BASE}${AUTH_LOGIN_PATH}/${provider}?frontRedirect=${encodeURIComponent(front)}`;
  };

  return (
    <div className="login-container">
      <h1 className="login-title">로그인</h1>

      <button className="login-btn kakao" disabled={loading} onClick={() => startSocial("kakao")}>
        <img src="/kakaotalk.png" className="login-icon" alt="카카오" />
        카카오로 시작하기
      </button>

      <button className="login-btn naver" disabled={loading} onClick={() => startSocial("naver")}>
        <img src="/naver.png" className="login-icon" alt="네이버" />
        네이버로 시작하기
      </button>

      <button className="login-btn google" disabled={loading} onClick={() => startSocial("google")}>
        <img src="/google.png" className="login-icon" alt="구글" />
        구글로 시작하기
      </button>

      {loading && <p style={{ marginTop: 12, fontSize: 14, opacity: 0.8 }}>{status}</p>}
    </div>
  );
}
