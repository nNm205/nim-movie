import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";

import Layout from "../components/Common/Layout";
import MovieCarousel from "../components/Movie/MovieCarousel";
import { movieService } from "../services/movieService";

const MovieListPage = () => {
  const location = useLocation();
  const { genreId } = useParams();

  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        setLoading(true);

        let response;

        switch (location.pathname) {
          case "/movies":
            setTitle("Danh sách phim");
            response = await movieService.getMovies(page);
            break;

          case "/movies/trending":
            setTitle("Phim Xu Hướng");
            response = await movieService.getTrending(page);
            break;

          case "/movies/popular":
            setTitle("Phim Phổ Biến");
            response = await movieService.getPopular(page);
            break;

          case "/movies/top-rated":
            setTitle("Phim Xếp Hạng Cao");
            response = await movieService.getTopRated(page);
            break;

          default:
            response = { items: [] };
        }

        setMovies(response.items || []);
        setTotalPages(response.totalPages || 1);
      } catch (error) {
        console.error("Error fetching movies:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, [location.pathname, genreId, page]);

  return (
    <Layout>
      <div className="bg-black min-h-screen text-white px-6 md:px-10 py-10">
        <div className="max-w-screen-2xl mx-auto">
          <h1 className="text-4xl font-bold mb-10">{title}</h1>

          <MovieCarousel movies={movies} loading={loading} />

          <div className="flex items-center justify-center gap-4 mt-10">
            <button
              disabled={page === 1}
              onClick={() => setPage((prev) => prev - 1)}
              className="px-4 py-2 rounded bg-zinc-800 text-white disabled:opacity-50"
            >
              Trang trước
            </button>

            <span className="text-zinc-400">
              Trang {page} / {totalPages}
            </span>

            <button
              disabled={page === totalPages}
              onClick={() => setPage((prev) => prev + 1)}
              className="px-4 py-2 rounded bg-zinc-800 text-white disabled:opacity-50"
            >
              Trang sau
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default MovieListPage;
