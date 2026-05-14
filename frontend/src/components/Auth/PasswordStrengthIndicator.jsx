const PasswordStrengthIndicator = ({ password, strength }) => {
  if (!password) return null;

  const getPasswordStrengthColor = () => {
    if (strength === 0) return "bg-zinc-700";
    if (strength === 1) return "bg-red-500";
    if (strength === 2) return "bg-orange-500";
    if (strength === 3) return "bg-yellow-500";
    return "bg-green-500";
  };

  const getPasswordStrengthText = () => {
    if (strength === 0) return "";
    if (strength === 1) return "Yếu";
    if (strength === 2) return "Trung bình";
    if (strength === 3) return "Khá";
    return "Mạnh";
  };

  return (
    <div className="mt-2">
      <div className="flex gap-1 mb-1">
        {[1, 2, 3, 4].map((level) => (
          <div
            key={level}
            className={`h-1 flex-1 rounded-full transition-colors ${
              level <= strength ? getPasswordStrengthColor() : "bg-zinc-700"
            }`}
          ></div>
        ))}
      </div>
      <p
        className={`text-xs ${
          strength >= 3
            ? "text-green-500"
            : strength === 2
              ? "text-yellow-500"
              : "text-red-500"
        }`}
      >
        {getPasswordStrengthText()}
      </p>
    </div>
  );
};

export default PasswordStrengthIndicator;
