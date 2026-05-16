import { useNavigate } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import MovieCard from "./MovieCard";

const MovieCarousel = ({
  title = "",
  movies = [],
  loading = false,
  viewMoreLink = null,
}) => {
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="text-white text-center py-10">Loading movies...</div>
    );
  }

  if (!movies.length) {
    return <div className="text-gray-400 py-10">No movies found</div>;
  }

  return (
    <div className="mb-12">
      {(title || viewMoreLink) && (
        <div className="flex items-center justify-between mb-6">
          {title ? (
            <h2 className="text-3xl font-bold text-white">{title}</h2>
          ) : (
            <div />
          )}

          {viewMoreLink && (
            <button
              onClick={() => navigate(viewMoreLink)}
              className="flex items-center gap-1 text-zinc-400 hover:text-white transition-colors group"
            >
              <span className="text-sm font-medium">Xem thêm</span>

              <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" />
            </button>
          )}
        </div>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
        {movies.map((movie) => (
          <MovieCard key={movie.id} movie={movie} />
        ))}
      </div>
    </div>
  );
};

export default MovieCarousel;
