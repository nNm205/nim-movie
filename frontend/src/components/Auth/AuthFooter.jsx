import { Link } from "react-router-dom";

const AuthFooter = () => {
  return (
    <p className="text-center text-zinc-500 text-xs mt-6">
      Bằng việc đăng nhập, bạn đồng ý với{" "}
      <Link
        to="/terms"
        className="text-zinc-400 hover:text-white transition-colors"
      >
        Điều khoản sử dụng
      </Link>{" "}
      và{" "}
      <Link
        to="/privacy"
        className="text-zinc-400 hover:text-white transition-colors"
      >
        Chính sách bảo mật
      </Link>
    </p>
  );
};

export default AuthFooter;
