export const validateRegistration = (newUser) => {
  if (
    !newUser.username ||
    !newUser.email ||
    !newUser.password ||
    !newUser.confirmPassword
  ) {
    return "Vui lòng điền đầy đủ thông tin";
  }

  if (newUser.username.length < 3) {
    return "Tên người dùng phải có ít nhất 3 ký tự";
  }

  if (newUser.password.length < 8) {
    return "Mật khẩu phải có ít nhất 8 ký tự";
  }

  if (newUser.password !== newUser.confirmPassword) {
    return "Mật khẩu xác nhận không khớp";
  }

  return null; // No error
};

export const calculatePasswordStrength = (password) => {
  let strength = 0;
  if (password.length >= 8) strength++;
  if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
  if (password.match(/[0-9]/)) strength++;
  if (password.match(/[^a-zA-Z0-9]/)) strength++;
  return strength;
};
