import { useNavigate } from "react-router-dom";
import { getBackdropUrl } from "../../utils/tmdb";

const HeroBanner = ({ movie, loading }) => {
  const navigate = useNavigate();

  if (loading || !movie) {
    return <div className="h-[600px] bg-zinc-900 animate-pulse" />;
  }

  return (
    <div
      className="relative h-[600px] bg-cover bg-center mt-2"
      style={{
        backgroundImage: `url(${getBackdropUrl(movie.backdrop_path)})`,
      }}
    >
      <div className="absolute inset-0 bg-black/60" />

      <div className="relative z-10 h-full flex items-center px-12">
        <div className="max-w-2xl">
          <h1 className="text-6xl font-bold text-white mb-6">{movie.title}</h1>

          <p className="text-gray-300 text-lg mb-8">{movie.overview}</p>

          <button
            onClick={() => navigate(`/movies/${movie.id}`)}
            className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded font-bold"
          >
            Xem thêm
          </button>
        </div>
      </div>
    </div>
  );
};

export default HeroBanner;
