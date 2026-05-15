import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Layout from "../components/Common/Layout";
import { movieService } from "../services/movieService";

const WatchPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMovie = async () => {
      try {
        setLoading(true);
        const data = await movieService.getMovieDetail(id);
        setMovie(data);
      } catch (err) {
        console.error("WatchPage error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchMovie();
  }, [id]);

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen text-zinc-400">
          Loading player...
        </div>
      </Layout>
    );
  }

  if (!movie) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen text-zinc-400">
          Không tìm thấy phim
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="w-full px-4 sm:px-6 lg:px-8 py-4 lg:py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="hidden lg:block lg:col-span-2">
            <button
              onClick={() => navigate(-1)}
              className="bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-2.5 rounded-lg transition duration-200 font-medium text-sm"
            >
              ← Quay lại
            </button>
          </div>

          <div className="col-span-1 lg:col-span-8 space-y-6">
            <div className="block lg:hidden">
              <button
                onClick={() => navigate(-1)}
                className="bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-2.5 rounded-lg transition"
              >
                ← Quay lại
              </button>
            </div>

            <div className="relative w-full aspect-video bg-black rounded-xl overflow-hidden shadow-2xl">
              <iframe
                className="w-full h-full"
                src={`https://vidsrc.icu/embed/movie/${id}`}
                allowFullScreen
                allow="autoplay"
                scrolling="no"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
            </div>

            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-white">
                {movie.title}
              </h1>

              <div className="flex flex-wrap items-center gap-3 mt-3 text-sm text-zinc-400">
                <span className="text-yellow-400 font-semibold">
                  ⭐ {movie.vote_average?.toFixed(1)}/10
                </span>

                <span className="w-1 h-1 bg-zinc-600 rounded-full" />

                <span>
                  {movie.release_date
                    ? new Date(movie.release_date).toLocaleDateString("vi-VN")
                    : "N/A"}
                </span>

                {movie.runtime && (
                  <>
                    <span className="w-1 h-1 bg-zinc-600 rounded-full" />
                    <span>{movie.runtime} phút</span>
                  </>
                )}
              </div>
            </div>

            <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6">
              <h2 className="text-lg font-bold text-white mb-3">Overview</h2>
              <p className="text-zinc-300 leading-relaxed">
                {movie.overview || "Không có mô tả."}
              </p>
            </div>
          </div>

          <div className="hidden lg:block lg:col-span-2" />
        </div>
      </div>
    </Layout>
  );
};

export default WatchPage;
