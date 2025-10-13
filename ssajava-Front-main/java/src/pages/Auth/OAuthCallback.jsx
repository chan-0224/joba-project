import React, { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";

export default function OAuthCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();

  useEffect(() => {
    const handleLogin = async () => {
      const accessToken = searchParams.get("token");
      const requiresSignup = searchParams.get("requires_signup") === "true";
      const signupToken = searchParams.get("signup_token");
      const email = searchParams.get("email");
      const error = searchParams.get("error");
      
      if (error) {
        console.error("소셜 로그인 에러:", error);
        alert("로그인 중 오류가 발생했습니다.");
        navigate("/login");
        return;
      }
      
      if (accessToken) {
        try {
          api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
          const meResponse = await api.get('/auth/me');
          const userData = meResponse.data;
          
          login(userData, accessToken);
          
          navigate("/home");
        } catch (err) {
          console.error("/auth/me 호출 실패:", err);
          alert("사용자 정보를 가져오는 데 실패했습니다.");
          delete api.defaults.headers.common['Authorization'];
          navigate("/login");
        }
        return;
      }

      if (requiresSignup && signupToken) {
        navigate("/signup2", {
          state: { signupToken, email }
        });
        return;
      }

      alert("로그인 처리 정보가 없습니다.");
      navigate("/login");
    };

    handleLogin();
  }, [navigate, searchParams, login]);

  return <div>로그인 처리 중…</div>;
}