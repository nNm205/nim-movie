import ErrorAlert from "./ErrorAlert";
import EmailInput from "./EmailInput";
import PasswordInput from "./PasswordInput";
import RememberMeCheckbox from "./RememberMeCheckbox";
import SubmitButton from "./SubmitButton";
import Divider from "./Divider";
import SocialLoginButtons from "./SocialLoginButtons";
import SignUpPrompt from "./SignUpPrompt";

const LoginForm = ({
  loginData,
  error,
  loading,
  onEmailChange,
  onPasswordChange,
  onSubmit,
}) => {
  return (
    <div className="bg-gradient-to-br from-zinc-900 to-zinc-800 rounded-2xl p-8 border border-zinc-800/50 shadow-2xl">
      <form onSubmit={onSubmit} className="space-y-6">
        <ErrorAlert message={error} />

        <EmailInput value={loginData.email} onChange={onEmailChange} />

        <PasswordInput value={loginData.password} onChange={onPasswordChange} />

        <RememberMeCheckbox />

        <SubmitButton loading={loading} />
      </form>

      <Divider />

      <SocialLoginButtons />

      <SignUpPrompt />
    </div>
  );
};

export default LoginForm;
