import { Link } from "react-router-dom";

const RememberMeCheckbox = () => {
  return (
    <div className="flex items-center justify-between">
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          className="w-4 h-4 rounded border-zinc-700 bg-zinc-800 text-red-600 focus:ring-2 focus:ring-red-500/20"
        />
        <span className="text-sm text-zinc-400">Ghi nhớ đăng nhập</span>
      </label>
      <Link
        to="/forgot-password"
        className="text-sm text-red-500 hover:text-red-400 transition-colors"
      >
        Quên mật khẩu?
      </Link>
    </div>
  );
};

export default RememberMeCheckbox;
