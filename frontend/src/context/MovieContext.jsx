import { createContext, useState } from "react";
import { movieService } from "../services/movieService";

export const MovieContext = createContext();

export const MovieProvider = ({ children }) => {
  const [trendingMovies, setTrendingMovies] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchTrendingMovies = async () => {
    try {
      setLoading(true);

      const data = await movieService.getTrending();

      setTrendingMovies(data.results || []);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MovieContext.Provider
      value={{
        trendingMovies,
        loading,
        fetchTrendingMovies,
      }}
    >
      {children}
    </MovieContext.Provider>
  );
};
