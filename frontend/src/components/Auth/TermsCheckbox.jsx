import { Link } from "react-router-dom";

const TermsCheckbox = () => {
  return (
    <div className="flex items-start gap-2">
      <input
        type="checkbox"
        id="terms"
        className="mt-1 w-4 h-4 rounded border-zinc-700 bg-zinc-800 text-red-600 focus:ring-2 focus:ring-red-500/20"
        required
      />
      <label htmlFor="terms" className="text-sm text-zinc-400">
        Tôi đồng ý với{" "}
        <Link
          to="/terms"
          className="text-red-500 hover:text-red-400 transition-colors"
        >
          Điều khoản sử dụng
        </Link>{" "}
        và{" "}
        <Link
          to="/privacy"
          className="text-red-500 hover:text-red-400 transition-colors"
        >
          Chính sách bảo mật
        </Link>
      </label>
    </div>
  );
};

export default TermsCheckbox;
