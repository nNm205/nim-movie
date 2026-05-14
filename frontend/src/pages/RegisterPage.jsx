import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../services/authService";
import { validateRegistration } from "../utils/registerUtils";
import AuthHeader from "../components/Auth/AuthHeader";
import RegisterForm from "../components/Auth/RegisterForm";

const RegisterPage = () => {
  const [newUser, setNewUser] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const navigate = useNavigate();

  const handleUsernameChange = (e) => {
    setNewUser({ ...newUser, username: e.target.value });
    setError("");
  };

  const handleEmailChange = (e) => {
    setNewUser({ ...newUser, email: e.target.value });
    setError("");
  };

  const handlePasswordChange = (e) => {
    setNewUser({ ...newUser, password: e.target.value });
    setError("");
  };

  const handleConfirmPasswordChange = (e) => {
    setNewUser({ ...newUser, confirmPassword: e.target.value });
    setError("");
  };

  const handlePasswordStrengthChange = (strength) => {
    setPasswordStrength(strength);
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    const validationError = validateRegistration(newUser);
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const responseData = await authService.register(newUser);
      console.log(responseData);

      navigate("/login");
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.message || "Đăng ký thất bại. Vui lòng thử lại.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <AuthHeader
          title="Tạo tài khoản mới"
          subtitle="Đăng ký để khám phá hàng ngàn bộ phim"
        />

        <RegisterForm
          registerData={newUser}
          error={error}
          loading={loading}
          onUsernameChange={handleUsernameChange}
          onEmailChange={handleEmailChange}
          onPasswordChange={handlePasswordChange}
          onConfirmPasswordChange={handleConfirmPasswordChange}
          onPasswordStrengthChange={handlePasswordStrengthChange}
          onSubmit={handleRegister}
        />
      </div>
    </div>
  );
};

export default RegisterPage;
