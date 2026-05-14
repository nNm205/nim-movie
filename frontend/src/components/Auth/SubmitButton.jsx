import { Loader2 } from "lucide-react";

const SubmitButton = ({
  loading,
  text = "Đăng nhập",
  loadingText = "Đang đăng nhập...",
}) => {
  return (
    <button
      type="submit"
      disabled={loading}
      className="w-full py-3 bg-gradient-to-r from-red-600 to-red-500 text-white font-semibold rounded-lg hover:from-red-500 hover:to-red-400 transition-all duration-300 shadow-lg shadow-red-500/30 hover:shadow-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
    >
      {loading ? (
        <>
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>{loadingText}</span>
        </>
      ) : (
        <span>{text}</span>
      )}
    </button>
  );
};

export default SubmitButton;
