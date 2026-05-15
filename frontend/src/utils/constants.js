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
  GET_WATCHLIST: "/users/watchlist",
  ADD_TO_WATCHLIST: (movieId) => `/users/watchlist/${movieId}`,
  REMOVE_FROM_WATCHLIST: (movieId) => `/users/watchlist/${movieId}`,

  // Reviews
  GET_MOVIE_REVIEWS: (movieId) => `/movies/${movieId}/reviews`,
  CREATE_REVIEW: (movieId) => `/movies/${movieId}/reviews`,
  UPDATE_REVIEW: (reviewId) => `/reviews/${reviewId}`,
  DELETE_REVIEW: (reviewId) => `/reviews/${reviewId}`,
  GET_USER_REVIEWS: "/users/reviews",
};

export const SORT_OPTIONS = [
  { value: "trending", label: "Trending" },
  { value: "newest", label: "Newest" },
  { value: "top-rated", label: "Top Rated" },
  { value: "popular", label: "Popular" },
];
