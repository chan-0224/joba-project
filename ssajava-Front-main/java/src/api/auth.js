/**
 * [설명]
 * - 인증 관련 API 호출 함수들.
 * - 상태 관리는 AuthContext에서 담당.
 */
import api from './client';

// 현재 토큰이 유효한지 서버에 물어보기 (예: 앱 시작 시 유효성 검증용)
export const verifyToken = () => api.get('/auth/verify');

// (선택) 리프레시 토큰으로 액세스 토큰 재발급받기 (서버 정책에 맞춰 호출)
export const refreshToken = (refreshToken) =>
  api.post('/auth/refresh', { refreshToken });

// 로그아웃은 AuthContext에서 처리하므로 여기서 삭제합니다.
