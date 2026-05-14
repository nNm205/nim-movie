import ErrorAlert from "./ErrorAlert";
import UsernameInput from "./UsernameInput";
import EmailInput from "./EmailInput";
import PasswordInputWithStrength from "./PasswordInputWithStrength";
import ConfirmPasswordInput from "./ConfirmPasswordInput";
import TermsCheckbox from "./TermsCheckbox";
import SubmitButton from "./SubmitButton";
import Divider from "./Divider";
import SocialLoginButtons from "./SocialLoginButtons";
import LoginPrompt from "./LoginPrompt";

const RegisterForm = ({
  registerData,
  error,
  loading,
  onUsernameChange,
  onEmailChange,
  onPasswordChange,
  onConfirmPasswordChange,
  onPasswordStrengthChange,
  onSubmit,
}) => {
  return (
    <div className="bg-gradient-to-br from-zinc-900 to-zinc-800 rounded-2xl p-8 border border-zinc-800/50 shadow-2xl">
      <form onSubmit={onSubmit} className="space-y-5">
        <ErrorAlert message={error} />

        <UsernameInput
          value={registerData.username}
          onChange={onUsernameChange}
        />

        <EmailInput value={registerData.email} onChange={onEmailChange} />

        <PasswordInputWithStrength
          value={registerData.password}
          onChange={onPasswordChange}
          onStrengthChange={onPasswordStrengthChange}
        />

        <ConfirmPasswordInput
          value={registerData.confirmPassword}
          onChange={onConfirmPasswordChange}
          password={registerData.password}
        />

        <TermsCheckbox />

        <SubmitButton
          loading={loading}
          text="Đăng ký"
          loadingText="Đang đăng ký..."
        />
      </form>

      <Divider text="Hoặc đăng ký với" />

      <SocialLoginButtons />

      <LoginPrompt />
    </div>
  );
};

export default RegisterForm;
