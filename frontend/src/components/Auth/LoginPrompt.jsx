import { Link } from "react-router-dom";

const LoginPrompt = () => {
  return (
    <div className="mt-6 text-center">
      <p className="text-zinc-400 text-sm">
        Đã có tài khoản?{" "}
        <Link
          to="/login"
          className="text-red-500 hover:text-red-400 font-semibold transition-colors"
        >
          Đăng nhập ngay
        </Link>
      </p>
    </div>
  );
};

export default LoginPrompt;
