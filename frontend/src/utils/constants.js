export const API_ENDPOINTS = {
  AUTH_LOGIN: "/auth/login",
  AUTH_REGISTER: "/auth/register",
  AUTH_LOGOUT: "/auth/logout",
  AUTH_REFRESH: "/auth/refresh-token",

  GET_PROFILE: "/users/profile",
  UPDATE_PROFILE: "/users/profile",

  GET_MOVIE_DETAIL: (id) => `/movies/${id}`,
  SEARCH_MOVIES: "/movies/search",
  GET_GENRES: "/movies/genres",
  GET_MOVIES: "/movies/discover",
  GET_TRENDING: "/movies/trending",
  GET_POPULAR: "/movies/popular",
  GET_TOP_RATED: "/movies/top-rated",

  GET_WATCHLIST: "/users/watchlist",
  ADD_TO_WATCHLIST: (movieId) => `/users/watchlist/${movieId}`,
  REMOVE_FROM_WATCHLIST: (movieId) => `/users/watchlist/${movieId}`,

  GET_MOVIE_REVIEWS: (movieId) => `/movies/${movieId}/reviews`,
  CREATE_REVIEW: (movieId) => `/movies/${movieId}/reviews`,
  UPDATE_REVIEW: (reviewId) => `/reviews/${reviewId}`,
  DELETE_REVIEW: (reviewId) => `/reviews/${reviewId}`,
  GET_USER_REVIEWS: "/users/reviews",
};

export const SORT_OPTIONS = [
  {
    value: "popularity.desc",
    label: "Phổ biến nhất",
  },
  {
    value: "vote_average.desc",
    label: "Đánh giá cao",
  },
  {
    value: "primary_release_date.desc",
    label: "Mới phát hành",
  },
  {
    value: "revenue.desc",
    label: "Doanh thu cao",
  },
  {
    value: "original_title.asc",
    label: "Tên A-Z",
  },
];

export const RATING_OPTIONS = [
  {
    value: "",
    label: "Tất cả đánh giá",
  },
  {
    value: 5,
    label: "5+ ⭐",
  },
  {
    value: 6,
    label: "6+ ⭐",
  },
  {
    value: 7,
    label: "7+ ⭐",
  },
  {
    value: 8,
    label: "8+ ⭐",
  },
];

export const YEAR_OPTIONS = Array.from(
  { length: 30 },
  (_, index) => new Date().getFullYear() - index,
);
