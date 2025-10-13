import axios from 'axios';

// 1. .env에서 두 변수를 모두 불러옵니다.
const BASE = import.meta.env.VITE_API_BASE_URL;
const PREFIX = import.meta.env.VITE_API_PREFIX;

// 2. 두 변수를 조합하여 완전한 API 기본 주소를 만듭니다.
const API_URL = `${BASE}${PREFIX}`;

const api = axios.create({
  baseURL: API_URL, // 3. 조합된 주소를 baseURL로 사용합니다.
  headers: { 'Content-Type': 'application/json' },
  withCredentials: false,
});

// 토큰 첨부 로직은 그대로 유지
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;