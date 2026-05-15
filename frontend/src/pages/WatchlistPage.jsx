import { useEffect, useState } from "react";
import Layout from "../components/Common/Layout";
import WatchlistCard from "../components/Watchlist/WatchlistCard";
import EmptyWatchlist from "../components/Watchlist/EmptyWatchlist";
import { watchlistService } from "../services/watchlistService";

const WatchlistPage = () => {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWatchlist = async () => {
      try {
        setLoading(true);

        const data = await watchlistService.getMyWatchlist();

        setWatchlist(data.items || []);
      } catch (error) {
        console.error("Failed to fetch watchlist:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchWatchlist();
  }, []);

  const handleRemove = async (movieId) => {
    const confirmed = window.confirm(
      "Bạn chắc chắn muốn bỏ lưu phim này khỏi danh sách xem sau?",
    );

    if (!confirmed) return;

    try {
      await watchlistService.removeFromWatchlist(movieId);

      setWatchlist((prev) =>
        prev.filter((movie) => movie.movie_id !== movieId),
      );
    } catch (error) {
      console.error(error);

      alert("Failed to remove movie");
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="bg-black text-white min-h-screen flex items-center justify-center">
          Đang tải danh sách phim...
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="bg-black text-white min-h-screen">
        <div className="max-w-screen-2xl mx-auto px-4 md:px-8 py-10">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold">
                Danh sách xem sau
              </h1>

              <p className="text-zinc-400 mt-3">
                {watchlist.length} phim được lưu
              </p>
            </div>
          </div>

          {watchlist.length === 0 ? (
            <EmptyWatchlist />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {watchlist.map((item) => (
                <WatchlistCard
                  key={item.movie_id}
                  item={item}
                  onRemove={handleRemove}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default WatchlistPage;
