import { useNavigate } from "react-router-dom";
import { getPosterUrl } from "../../utils/tmdb";

const MovieCard = ({ movie }) => {
  const navigate = useNavigate();

  return (
    <div
      className="cursor-pointer group"
      onClick={() => navigate(`/movies/${movie.id}`)}
    >
      <div className="overflow-hidden rounded-xl bg-zinc-900">
        <img
          src={getPosterUrl(movie.poster_path)}
          alt={movie.title}
          className="w-full aspect-[2/3] object-cover group-hover:scale-110 transition duration-300"
        />
      </div>

      <h3 className="mt-3 text-white font-semibold line-clamp-1">
        {movie.title}
      </h3>

      <div className="flex items-center gap-2 text-sm text-gray-400 mt-1">
        <span>⭐ {movie.vote_average?.toFixed(1)}</span>

        <span>
          {movie.release_date ? movie.release_date.slice(0, 4) : "N/A"}
        </span>
      </div>
    </div>
  );
};

export default MovieCard;
