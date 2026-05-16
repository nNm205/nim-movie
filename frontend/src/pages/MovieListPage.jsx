import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

import Layout from "../components/Common/Layout";
import MovieCarousel from "../components/Movie/MovieCarousel";
import { movieService } from "../services/movieService";
import FilterDropdown from "../components/Common/FilterDropdown";
import { SORT_OPTIONS, RATING_OPTIONS, YEAR_OPTIONS } from "../utils/constants";

const MovieListPage = () => {
  const location = useLocation();

  const [movies, setMovies] = useState([]);
  const [genres, setGenres] = useState([]);

  const [loading, setLoading] = useState(true);

  const [title, setTitle] = useState("");

  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const [filters, setFilters] = useState({
    genreId: "",
    sortBy: "popularity.desc",
    year: "",
    rating: "",
  });

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const data = await movieService.getGenres();
        setGenres(data || []);
      } catch (error) {
        console.error("Error fetching genres:", error);
      }
    };

    fetchGenres();
  }, []);

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        setLoading(true);

        let response;

        switch (location.pathname) {
          case "/movies":
            setTitle("Danh sách phim");

            response = await movieService.getMovies({
              page,
              ...filters,
            });

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
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, [location.pathname, page, filters]);

  return (
    <Layout>
      <div className="bg-black min-h-screen text-white px-6 md:px-10 py-10">
        <div className="max-w-screen-2xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6 mb-10">
            <h1 className="text-4xl font-bold">{title}</h1>

            {location.pathname === "/movies" && (
              <div className="flex flex-wrap gap-4">
                <FilterDropdown
                  label="Thể loại"
                  value={filters.genreId}
                  onChange={(value) => {
                    setPage(1);

                    setFilters((prev) => ({
                      ...prev,
                      genreId: value,
                    }));
                  }}
                  options={[
                    {
                      value: "",
                      label: "Tất cả thể loại",
                    },

                    ...genres.map((genre) => ({
                      value: genre.id,
                      label: genre.name,
                    })),
                  ]}
                />

                <FilterDropdown
                  label="Sắp xếp"
                  value={filters.sortBy}
                  onChange={(value) => {
                    setPage(1);

                    setFilters((prev) => ({
                      ...prev,
                      sortBy: value,
                    }));
                  }}
                  options={SORT_OPTIONS}
                />

                <FilterDropdown
                  label="Năm phát hành"
                  value={filters.year}
                  onChange={(value) => {
                    setPage(1);

                    setFilters((prev) => ({
                      ...prev,
                      year: value,
                    }));
                  }}
                  options={[
                    {
                      value: "",
                      label: "Tất cả năm",
                    },

                    ...YEAR_OPTIONS.map((year) => ({
                      value: year,
                      label: year,
                    })),
                  ]}
                />

                <FilterDropdown
                  label="Đánh giá"
                  value={filters.rating}
                  onChange={(value) => {
                    setPage(1);

                    setFilters((prev) => ({
                      ...prev,
                      rating: value,
                    }));
                  }}
                  options={RATING_OPTIONS}
                />
              </div>
            )}
          </div>

          <MovieCarousel movies={movies} loading={loading} />

          <div className="flex items-center justify-center gap-4 mt-10">
            <button
              disabled={page === 1}
              onClick={() => setPage((prev) => prev - 1)}
              className="px-4 py-2 rounded bg-zinc-800 hover:bg-zinc-700 transition disabled:opacity-50"
            >
              Trang trước
            </button>

            <span className="text-zinc-400">
              Trang {page} / {totalPages}
            </span>

            <button
              disabled={page === totalPages}
              onClick={() => setPage((prev) => prev + 1)}
              className="px-4 py-2 rounded bg-zinc-800 hover:bg-zinc-700 transition disabled:opacity-50"
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
