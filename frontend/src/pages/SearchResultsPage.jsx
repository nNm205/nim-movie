import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import Layout from "../components/Common/Layout";
import MovieCarousel from "../components/Movie/MovieCarousel";
import { movieService } from "../services/movieService";

const SearchResultPage = () => {
  const [searchParams] = useSearchParams();

  const query = searchParams.get("q") || "";

  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSearchResults = async () => {
      if (!query) return;

      try {
        setLoading(true);

        const response = await movieService.searchMovies(query);

        setMovies(response.items || response.results || []);
      } catch (error) {
        console.error("Search error:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchSearchResults();
  }, [query]);

  return (
    <Layout>
      <div className="bg-black min-h-screen text-white">
        <div className="max-w-screen-2xl mx-8 px-4 md:px-8">
          {/* Header */}
          <div className="mb-10">
            <h1 className="text-3xl md:text-5xl font-bold mb-4">
              Kết quả tìm kiếm
            </h1>

            <div className="flex flex-wrap items-center gap-3 text-zinc-400">
              <span>
                Từ khóa:
                <span className="text-red-500 font-semibold ml-2">
                  "{query}"
                </span>
              </span>

              {!loading && (
                <>
                  <span className="text-zinc-600">•</span>

                  <span>
                    Tìm thấy
                    <span className="text-white font-semibold mx-2">
                      {movies.length}
                    </span>
                    kết quả
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Loading */}
          {loading && (
            <div className="text-zinc-400 text-lg">Đang tìm kiếm phim...</div>
          )}

          {/* Empty State */}
          {!loading && movies.length === 0 && (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <h2 className="text-2xl font-bold mb-4">
                Không tìm thấy kết quả
              </h2>

              <p className="text-zinc-400 max-w-lg leading-7">
                Không có phim nào phù hợp với từ khóa
                <span className="text-red-500 mx-2">"{query}"</span>. Hãy thử
                tìm kiếm với tên khác.
              </p>
            </div>
          )}

          {/* Results */}
          {!loading && movies.length > 0 && (
            <MovieCarousel title="" movies={movies} loading={loading} />
          )}
        </div>
      </div>
    </Layout>
  );
};

export default SearchResultPage;
