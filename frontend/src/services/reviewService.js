import api from "../utils/api";
import { API_ENDPOINTS } from "../utils/constants";

export const reviewService = {
  async getMovieReviews(movieId) {
    try {
      const response = await api.get(API_ENDPOINTS.GET_MOVIE_REVIEWS(movieId));

      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Failed to fetch movie reviews";
    }
  },

  async createReview(movieId, reviewData) {
    try {
      const response = await api.post(
        API_ENDPOINTS.CREATE_REVIEW(movieId),
        reviewData,
      );

      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Failed to create review";
    }
  },

  async updateReview(reviewId, reviewData) {
    try {
      const response = await api.put(
        API_ENDPOINTS.UPDATE_REVIEW(reviewId),
        reviewData,
      );

      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Failed to update review";
    }
  },

  async deleteReview(reviewId) {
    try {
      const response = await api.delete(API_ENDPOINTS.DELETE_REVIEW(reviewId));

      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Failed to delete review";
    }
  },

  async getMyReviews(page = 1, pageSize = 20) {
    try {
      const response = await api.get(API_ENDPOINTS.GET_USER_REVIEWS, {
        params: { page, pageSize },
      });

      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Failed to fetch user reviews";
    }
  },
};
