import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import Layout from "../components/Common/Layout";
import { movieService } from "../services/movieService";
import { getPosterUrl, getBackdropUrl } from "../utils/tmdb";
import ReviewSection from "../components/Review/ReviewSection";
import WatchlistButton from "../components/Watchlist/WatchlistButton";

const MovieDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [id]);

  useEffect(() => {
    const fetchMovie = async () => {
      try {
        setLoading(true);

        const data = await movieService.getMovieDetail(id);

        setMovie(data);
      } catch (error) {
        console.error("Error fetching movie:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMovie();
  }, [id]);

  if (loading) {
    return (
      <Layout>
        <div className="text-white text-center py-20">Loading movie...</div>
      </Layout>
    );
  }

  if (!movie) {
    return (
      <Layout>
        <div className="text-center text-white py-20">
          <p>Không tìm thấy phim</p>

          <button
            onClick={() => navigate("/")}
            className="bg-red-600 px-5 py-2 rounded mt-5"
          >
            Quay lại
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="bg-black text-white min-h-screen">
        <div className="relative h-[70vh]">
          <img
            src={getBackdropUrl(movie.backdrop_path)}
            alt={movie.title}
            className="w-full h-full object-cover"
          />

          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/70 to-black/30" />
        </div>

        <div className="max-w-screen-2xl mx-8 px-4 md:px-8 lg:px-12 -mt-52 relative z-10 pb-32">
          <button
            onClick={() => navigate("/")}
            className="mb-8 bg-black/70 hover:bg-red-600 px-5 py-2 rounded-lg transition duration-300"
          >
            Quay lại
          </button>

          <div className="grid md:grid-cols-3 gap-10 lg:gap-14">
            <div>
              <img
                src={getPosterUrl(movie.poster_path)}
                alt={movie.title}
                className="rounded-2xl shadow-2xl w-full"
              />
            </div>

            <div className="md:col-span-2">
              <h1 className="text-4xl md:text-6xl font-bold mb-6">
                {movie.title}
              </h1>

              <div className="flex flex-wrap gap-5 text-gray-300 mb-6 text-sm md:text-base">
                <span>{movie.release_date}</span>

                <span>⭐ {movie.vote_average?.toFixed(1)}</span>

                <span>{movie.runtime} min</span>
              </div>

              <div className="flex flex-wrap gap-3 mb-8">
                {movie.genres?.map((genre) => (
                  <span
                    key={genre.id}
                    className="bg-red-600/90 px-4 py-2 rounded-full text-sm"
                  >
                    {genre.name}
                  </span>
                ))}
              </div>

              <p className="text-gray-300 leading-8 text-base md:text-lg">
                {movie.overview}
              </p>

              <div className="flex gap-4 mt-10">
                <Link
                  to={`/watch/${movie.id}`}
                  className="bg-red-600 hover:bg-red-700 px-8 py-4 rounded-lg font-semibold transition duration-300"
                >
                  Xem ngay
                </Link>

                <WatchlistButton movieId={movie.id} />
              </div>
            </div>
          </div>

          <div className="mt-24">
            <h2 className="text-3xl font-bold mb-8">Diễn viên</h2>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-5">
              {movie.cast?.slice(0, 12).map((actor) => (
                <div
                  key={actor.id}
                  className="bg-zinc-900 hover:bg-zinc-800 transition duration-300 p-4 rounded-2xl"
                >
                  <h3 className="font-semibold text-white">{actor.name}</h3>

                  <p className="text-gray-400 text-sm mt-2">
                    {actor.character}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-24 border-t border-zinc-800 pt-16">
            <ReviewSection movieId={movie.id} />
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default MovieDetailPage;
