import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../services/authService";
import { useAuth } from "../hooks/useAuth";
import AuthHeader from "../components/Auth/AuthHeader";
import LoginForm from "../components/Auth/LoginForm";
import AuthFooter from "../components/Auth/AuthFooter";

const LoginPage = () => {
  const [loginData, setLoginData] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleEmailChange = (e) => {
    setLoginData({ ...loginData, email: e.target.value });
    setError("");
  };

  const handlePasswordChange = (e) => {
    setLoginData({ ...loginData, password: e.target.value });
    setError("");
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!loginData.email || !loginData.password) {
      setError("Vui lòng điền đầy đủ thông tin đăng nhập");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const responseData = await authService.login(loginData);

      login(responseData.user);
      navigate("/");

      setLoginData({ email: "", password: "" });
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.message ||
          "Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin đăng nhập.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <AuthHeader
          title="Chào mừng trở lại!"
          subtitle="Đăng nhập để tiếp tục xem phim"
        />

        <LoginForm
          loginData={loginData}
          error={error}
          loading={loading}
          onEmailChange={handleEmailChange}
          onPasswordChange={handlePasswordChange}
          onSubmit={handleLogin}
        />

        <AuthFooter />
      </div>
    </div>
  );
};

export default LoginPage;
