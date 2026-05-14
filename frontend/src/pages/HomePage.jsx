import { useState, useEffect } from "react";
import Layout from "../components/Common/Layout";
import HeroBanner from "../components/Home/HeroBanner";
import MovieCarousel from "../components/Movie/MovieCarousel";
import { movieService } from "../services/movieService";

const HomePage = () => {
  const [heroMovie, setHeroMovie] = useState(null);
  const [trendingMovies, setTrendingMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        setLoading(true);

        const response = await movieService.getTrending();

        const movies = response.items || [];

        setTrendingMovies(movies);

        if (movies.length > 0) {
          setHeroMovie(movies[0]);
        }
      } catch (error) {
        console.error("Error fetching movies:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, []);

  return (
    <Layout>
      <div className="bg-black text-white">
        <HeroBanner movie={heroMovie} loading={loading} />

        <section className="max-w-screen-2xl mx-8 px-4 py-12">
          <MovieCarousel
            title="Trending Movies"
            movies={trendingMovies}
            loading={loading}
          />
        </section>
      </div>
    </Layout>
  );
};

export default HomePage;
