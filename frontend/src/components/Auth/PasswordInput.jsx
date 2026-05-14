import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

const PasswordInput = ({
  value,
  onChange,
  label = "Mật khẩu",
  placeholder = "••••••••",
}) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div>
      <label className="block text-sm font-medium text-zinc-300 mb-2">
        {label}
      </label>
      <div className="relative">
        <input
          type={showPassword ? "text" : "password"}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className="w-full pl-4 pr-12 py-3 bg-zinc-800/50 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-red-500 focus:ring-2 focus:ring-red-500/20 transition-all"
          required
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute inset-y-0 right-0 pr-4 flex items-center text-zinc-500 hover:text-white transition-colors"
        >
          {showPassword ? (
            <EyeOff className="w-5 h-5" />
          ) : (
            <Eye className="w-5 h-5" />
          )}
        </button>
      </div>
    </div>
  );
};

export default PasswordInput;
