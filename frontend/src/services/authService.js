import api from "../utils/api";
import { API_ENDPOINTS } from "../utils/constants";
import Cookies from "js-cookie";

export const authService = {
  async login(loginData) {
    try {
      const response = await api.post(API_ENDPOINTS.AUTH_LOGIN, {
        email: loginData.email,
        password: loginData.password,
      });

      const { access_token, user } = response.data;

      Cookies.set("token", access_token, { expires: 7 });
      Cookies.set("user", JSON.stringify(user), { expires: 7 });

      return { access_token, user };
    } catch (error) {
      console.log("LOGIN ERROR:", error.response?.data);
      throw error.response?.data?.message || "Login failed";
    }
  },

  async register(registerData) {
    try {
      const response = await api.post(API_ENDPOINTS.AUTH_REGISTER, {
        username: registerData.username,
        email: registerData.email,
        password: registerData.password,
        confirm_password: registerData.confirmPassword,
      });

      const { access_token, user } = response.data;

      Cookies.set("token", access_token, { expires: 7 });
      Cookies.set("user", JSON.stringify(user), { expires: 7 });

      return { access_token, user };
    } catch (error) {
      console.log("REGISTER ERROR:", error.response?.data);
      throw error.response?.data?.message || "Registration failed";
    }
  },

  logout() {
    Cookies.remove("token");
    Cookies.remove("user");
  },

  getToken() {
    return Cookies.get("token");
  },

  getUser() {
    const user = Cookies.get("user");
    return user ? JSON.parse(user) : null;
  },

  isAuthenticated() {
    return !!this.getToken();
  },
};
