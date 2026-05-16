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

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        setLoading(true);

        let response;

        switch (location.pathname) {
          case "/movies":
            setTitle("Danh sách phim");
            response = await movieService.getMovies();
            break;

          case "/movies/trending":
            setTitle("Phim Xu Hướng");
            response = await movieService.getTrending();
            break;

          case "/movies/popular":
            setTitle("Phim Phổ Biến");
            response = await movieService.getPopular();
            break;

          case "/movies/top-rated":
            setTitle("Phim Xếp Hạng Cao");
            response = await movieService.getTopRated();
            break;

          default:
            response = { items: [] };
        }

        setMovies(response.items || []);
      } catch (error) {
        console.error("Error fetching movies:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, [location.pathname, genreId]);

  return (
    <Layout>
      <div className="bg-black min-h-screen text-white px-6 md:px-10 py-10">
        <div className="max-w-screen-2xl mx-auto">
          <h1 className="text-4xl font-bold mb-10">{title}</h1>

          <MovieCarousel title="" movies={movies} loading={loading} />
        </div>
      </div>
    </Layout>
  );
};

export default MovieListPage;
