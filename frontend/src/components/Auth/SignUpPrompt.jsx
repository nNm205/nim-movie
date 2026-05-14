import { Link } from "react-router-dom";

const SignUpPrompt = () => {
  return (
    <div className="mt-6 text-center">
      <p className="text-zinc-400 text-sm">
        Chưa có tài khoản?{" "}
        <Link
          to="/register"
          className="text-red-500 hover:text-red-400 font-semibold transition-colors"
        >
          Đăng ký ngay
        </Link>
      </p>
    </div>
  );
};

export default SignUpPrompt;
