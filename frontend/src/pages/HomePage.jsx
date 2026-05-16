import { useState, useEffect } from "react";
import Layout from "../components/Common/Layout";
import HeroBanner from "../components/Home/HeroBanner";
import MovieCarousel from "../components/Movie/MovieCarousel";
import { movieService } from "../services/movieService";

const HomePage = () => {
  const [heroMovie, setHeroMovie] = useState(null);
  const [trendingMovies, setTrendingMovies] = useState([]);
  const [popularMovies, setPopularMovies] = useState([]);
  const [topRatedMovies, setTopRatedMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        setLoading(true);

        const [trendingResponse, popularResponse, topRatedResponse] =
          await Promise.all([
            movieService.getTrending(),
            movieService.getPopular(),
            movieService.getTopRated(),
          ]);

        const trending = trendingResponse.items || [];
        const popular = popularResponse.items || [];
        const topRated = topRatedResponse.items || [];

        setTrendingMovies(trending);
        setPopularMovies(popular);
        setTopRatedMovies(topRated);

        if (trending.length > 0) {
          const randomMovie =
            trending[Math.floor(Math.random() * trending.length)];
          setHeroMovie(randomMovie);
        }
      } catch (error) {
        console.error("Error fetching homepage movies:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, []);

  return (
    <Layout>
      <div className="bg-black min-h-screen text-white overflow-hidden">
        <HeroBanner movie={heroMovie} loading={loading} />

        <div className="relative z-20 mt-10">
          <section className="space-y-14 px-4 md:px-8 lg:px-12 pb-16">
            <MovieCarousel
              title="Trending Now"
              movies={trendingMovies}
              loading={loading}
            />

            <MovieCarousel
              title="Popular Movies"
              movies={popularMovies}
              loading={loading}
            />

            <MovieCarousel
              title="Top Rated"
              movies={topRatedMovies}
              loading={loading}
            />
          </section>
        </div>
      </div>
    </Layout>
  );
};

export default HomePage;
