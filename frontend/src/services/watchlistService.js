import api from "../utils/api";
import { API_ENDPOINTS } from "../utils/constants";

export const watchlistService = {
  async getMyWatchlist(page = 1, pageSize = 20) {
    try {
      const response = await api.get(API_ENDPOINTS.GET_WATCHLIST, {
        params: { page, pageSize },
      });

      return response.data;
    } catch (error) {
      throw error.response?.data?.message || "Failed to fetch watchlist";
    }
  },

  async addToWatchlist(movieId) {
    try {
      const response = await api.post(API_ENDPOINTS.ADD_TO_WATCHLIST(movieId));

      return response.data;
    } catch (error) {
      throw error.response?.data?.message || "Failed to add movie to watchlist";
    }
  },

  async removeFromWatchlist(movieId) {
    try {
      const response = await api.delete(
        API_ENDPOINTS.REMOVE_FROM_WATCHLIST(movieId),
      );

      return response.data;
    } catch (error) {
      throw (
        error.response?.data?.message || "Failed to remove movie from watchlist"
      );
    }
  },

  async checkInWatchlist(movieId) {
    try {
      const response = await this.getMyWatchlist();

      const exists = response.items?.some((item) => item.movie_id === movieId);

      return exists;
    } catch (error) {
      console.error(error);

      return false;
    }
  },
};
