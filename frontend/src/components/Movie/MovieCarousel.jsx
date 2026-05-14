import MovieCard from "./MovieCard";

const MovieCarousel = ({ title, movies = [], loading = false }) => {
  if (loading) {
    return (
      <div className="text-white text-center py-10">Loading movies...</div>
    );
  }

  if (!movies.length) {
    return <div className="text-gray-400">No movies found</div>;
  }

  return (
    <div className="mb-12">
      <h2 className="text-3xl font-bold text-white mb-6">{title}</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-5">
        {movies.map((movie) => (
          <MovieCard key={movie.id} movie={movie} />
        ))}
      </div>
    </div>
  );
};

export default MovieCarousel;
