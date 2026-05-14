import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import PasswordStrengthIndicator from "./PasswordStrengthIndicator";

const PasswordInputWithStrength = ({ value, onChange, onStrengthChange }) => {
  const [showPassword, setShowPassword] = useState(false);

  const calculateStrength = (password = "") => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;
    return strength;
  };

  const handleChange = (e) => {
    const password = e.target.value;
    const strength = calculateStrength(password);
    if (onStrengthChange) {
      onStrengthChange(strength);
    }
    onChange(e);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-zinc-300 mb-2">
        Mật khẩu
      </label>
      <div className="relative">
        <input
          type={showPassword ? "text" : "password"}
          placeholder="••••••••"
          value={value}
          onChange={handleChange}
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

      <PasswordStrengthIndicator
        password={value || ""}
        strength={calculateStrength(value)}
      />
    </div>
  );
};

export default PasswordInputWithStrength;
