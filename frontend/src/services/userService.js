import api from "../utils/api";
import { API_ENDPOINTS } from "../utils/constants";

export const userService = {
  async getProfile() {
    try {
      const response = await api.get(API_ENDPOINTS.GET_PROFILE);
      console.log(response.data);

      return response.data;
    } catch (error) {
      throw error.response?.data?.message || "Failed to fetch profile";
    }
  },

  async updateProfile(data) {
    try {
      const response = await api.put(API_ENDPOINTS.UPDATE_PROFILE, data);

      return response.data;
    } catch (error) {
      throw error.response?.data?.message || "Failed to update profile";
    }
  },
};
