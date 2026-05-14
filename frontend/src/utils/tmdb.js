export const getPosterUrl = (path) => {
  if (!path) {
    return "https://placehold.co/500x750?text=No+Image";
  }

  return `https://image.tmdb.org/t/p/w500${path}`;
};

export const getBackdropUrl = (path) => {
  if (!path) {
    return "https://placehold.co/1280x720?text=No+Backdrop";
  }

  return `https://image.tmdb.org/t/p/original${path}`;
};
