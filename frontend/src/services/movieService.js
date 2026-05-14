import api from "../utils/api";
import { API_ENDPOINTS } from "../utils/constants";

export const movieService = {
  // async getMovies(page = 1, limit = 20) {
  //   try {
  //     const response = await api.get(API_ENDPOINTS.GET_MOVIES, {
  //       params: { page, limit },
  //     });

  //     return response.data;
  //   } catch (error) {
  //     throw error.response?.data?.message || "Failed to fetch movies";
  //   }
  // },

  async getTrending(page = 1, timeWindow = "week") {
    try {
      const response = await api.get(API_ENDPOINTS.GET_TRENDING, {
        params: { page, timeWindow },
      });

      return response.data;
    } catch (error) {
      throw error.response?.data?.message || "Failed to fetch trending movies";
    }
  },

  // async getByGenre(genre, limit = 10) {
  //   try {
  //     const response = await api.get(API_ENDPOINTS.GET_BY_GENRE(genre), {
  //       params: { limit },
  //     });

  //     return response.data;
  //   } catch (error) {
  //     throw error.response?.data?.message || `Failed to fetch ${genre} movies`;
  //   }
  // },

  async getMovieDetail(id) {
    try {
      const response = await api.get(API_ENDPOINTS.GET_MOVIE_DETAIL(id));
      return response.data;
    } catch (error) {
      throw error.response?.data?.message || "Failed to fetch movie detail";
    }
  },

  async searchMovies(q, page = 1) {
    try {
      const response = await api.get(API_ENDPOINTS.SEARCH_MOVIES, {
        params: { q, page },
      });

      return response.data;
    } catch (error) {
      throw error.response?.data?.message || "Failed to search movies";
    }
  },

  // async getRecommended(limit = 10) {
  //   try {
  //     const response = await api.get(
  //       `${API_ENDPOINTS.GET_MOVIES}?sort=-rating&limit=${limit}`,
  //     );

  //     return response.data;
  //   } catch (error) {
  //     throw (
  //       error.response?.data?.message || "Failed to fetch recommended movies"
  //     );
  //   }
  // },

  async getGenres() {
    try {
      const response = await api.get(API_ENDPOINTS.GET_GENRES);

      return response.data;
    } catch (error) {
      throw error.response?.data?.message || "Failed to fetch genres";
    }
  },
};
