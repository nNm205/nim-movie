import { Link } from "react-router-dom";
import { Trash2, Calendar, CheckCircle } from "lucide-react";
import { getPosterUrl } from "../../utils/tmdb";

const WatchlistCard = ({ item, onRemove }) => {
  return (
    <div className="group bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden hover:border-red-500/40 hover:bg-zinc-800 transition-all duration-300">
      <div className="relative overflow-hidden">
        <img
          src={getPosterUrl(item.poster_path)}
          alt={item.title}
          className="w-full h-[360px] object-cover group-hover:scale-105 transition duration-500"
        />

        {item.is_completed && (
          <div className="absolute top-3 right-3 bg-green-500 text-white p-2 rounded-full shadow-lg">
            <CheckCircle className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="p-5">
        <h3 className="text-white font-bold text-lg line-clamp-1">
          {item.title}
        </h3>

        <div className="flex items-center justify-between mt-3 text-sm text-zinc-400">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />

            <span>{new Date(item.added_at).toLocaleDateString()}</span>
          </div>

          <span>{item.progress}% đã xem</span>
        </div>

        <div className="flex gap-3 mt-5">
          <Link
            to={`/movies/${item.movie_id}`}
            className="flex-1 text-center bg-red-600 hover:bg-red-700 text-white py-2.5 rounded-lg font-semibold transition"
          >
            Xem phim
          </Link>

          <button
            onClick={() => onRemove(item.movie_id)}
            className="bg-zinc-800 hover:bg-zinc-700 text-red-400 hover:text-red-300 px-4 rounded-lg transition"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default WatchlistCard;
