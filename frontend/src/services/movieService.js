import api from "../utils/api";
import { API_ENDPOINTS } from "../utils/constants";

const handleError = (error, fallbackMessage) => {
  console.error(error);

  throw new Error(
    error.response?.data?.message || error.message || fallbackMessage,
  );
};

export const movieService = {
  async getMovies(page = 1, sort_by = "popularity.desc") {
    try {
      const response = await api.get(API_ENDPOINTS.GET_MOVIES, {
        params: { page, sort_by },
      });

      return response.data;
    } catch (error) {
      handleError(error, "Failed to fetch movies");
    }
  },

  async getTrending(page = 1, timeWindow = "week") {
    try {
      const response = await api.get(API_ENDPOINTS.GET_TRENDING, {
        params: { page, timeWindow },
      });

      return response.data;
    } catch (error) {
      handleError(error, "Failed to fetch trending movies");
    }
  },

  async getPopular(page = 1) {
    try {
      const response = await api.get(API_ENDPOINTS.GET_POPULAR, {
        params: { page },
      });

      return response.data;
    } catch (error) {
      handleError(error, "Failed to fetch popular movies");
    }
  },

  async getTopRated(page = 1) {
    try {
      const response = await api.get(API_ENDPOINTS.GET_TOP_RATED, {
        params: { page },
      });

      return response.data;
    } catch (error) {
      handleError(error, "Failed to fetch top rated movies");
    }
  },

  async getMovieDetail(id) {
    try {
      const response = await api.get(API_ENDPOINTS.GET_MOVIE_DETAIL(id));
      return response.data;
    } catch (error) {
      handleError(error, "Failed to fetch movie detail");
    }
  },

  async searchMovies(q, page = 1) {
    try {
      const response = await api.get(API_ENDPOINTS.SEARCH_MOVIES, {
        params: { q, page },
      });

      return response.data;
    } catch (error) {
      handleError(error, "Failed to search movies");
    }
  },

  async getGenres() {
    try {
      const response = await api.get(API_ENDPOINTS.GET_GENRES);

      return response.data;
    } catch (error) {
      handleError(error, "Failed to fetch genres");
    }
  },
};
