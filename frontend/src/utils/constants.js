export const API_ENDPOINTS = {
  // Auth
  AUTH_LOGIN: "/auth/login",
  AUTH_REGISTER: "/auth/register",
  AUTH_LOGOUT: "/auth/logout",
  AUTH_REFRESH: "/auth/refresh-token",

  // Users
  GET_PROFILE: "/users/profile",
  UPDATE_PROFILE: "/users/profile",

  // Movies
  // GET_MOVIES: "/movies",
  GET_MOVIE_DETAIL: (id) => `/movies/${id}`,
  SEARCH_MOVIES: "/movies/search",
  GET_TRENDING: "/movies/trending",
  GET_GENRES: "/movies/genres",
  // GET_BY_GENRE: (genre) => `/movies/genre/${genre}`,

  // Watchlist
  GET_WATCHLIST: "/watchlist",
  ADD_WATCHLIST: "/watchlist",
  REMOVE_WATCHLIST: (movieId) => `/watchlist/${movieId}`,

  // Reviews
  GET_REVIEWS: (movieId) => `/reviews/movie/${movieId}`,
  CREATE_REVIEW: "/reviews",
  UPDATE_REVIEW: (reviewId) => `/reviews/${reviewId}`,
  DELETE_REVIEW: (reviewId) => `/reviews/${reviewId}`,
};

export const SORT_OPTIONS = [
  { value: "trending", label: "Trending" },
  { value: "newest", label: "Newest" },
  { value: "top-rated", label: "Top Rated" },
  { value: "popular", label: "Popular" },
];
