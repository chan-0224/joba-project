import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('accessToken'));
  const [loading, setLoading] = useState(true);

  const login = useCallback((userData, accessToken) => {
    console.log("AuthContext: login 함수가 받은 데이터:", userData); 

    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('userProfile', JSON.stringify(userData));
    localStorage.setItem('currentUserId', userData.user_id);
    setToken(accessToken);
    setUser(userData);
    api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userProfile');
    localStorage.removeItem('currentUserId');
    setToken(null);
    setUser(null);
    delete api.defaults.headers.common['Authorization'];
  }, []);

  const updateUser = useCallback((newUserData) => {
    const currentProfile = JSON.parse(localStorage.getItem("userProfile") || "{}");
    const updatedProfile = { ...currentProfile, ...newUserData };
    localStorage.setItem('userProfile', JSON.stringify(updatedProfile));
    setUser(updatedProfile);
  }, []);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          const response = await api.get('/auth/me');
          const userData = response.data;
          // 토큰이 유효하므로 로그인 상태 유지
          setUser(userData);
        } catch (error) {
          console.error("세션이 만료되었거나 유효하지 않습니다.", error);
          logout(); // 유효하지 않은 토큰 정보 정리
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [token, logout]);

  const value = { user, token, loading, login, logout, updateUser };

  // 로딩 중에는 앱 콘텐츠를 렌더링하지 않아, 인증 정보가 확정된 후 화면을 보여줍니다.
  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};