import { useEffect, useState } from "react";
import { Bookmark, Check } from "lucide-react";
import { watchlistService } from "../../services/watchlistService";

const WatchlistButton = ({ movieId }) => {
  const [isInWatchlist, setIsInWatchlist] = useState(false);
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const checkWatchlistStatus = async () => {
      try {
        setChecking(true);

        const exists = await watchlistService.checkInWatchlist(movieId);

        setIsInWatchlist(exists);
      } catch (error) {
        console.error(error);
      } finally {
        setChecking(false);
      }
    };

    checkWatchlistStatus();
  }, [movieId]);

  const handleToggleWatchlist = async () => {
    try {
      setLoading(true);

      if (isInWatchlist) {
        await watchlistService.removeFromWatchlist(movieId);

        setIsInWatchlist(false);
      } else {
        await watchlistService.addToWatchlist(movieId);

        setIsInWatchlist(true);
      }
    } catch (error) {
      console.error(error);

      alert(error?.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  if (checking) {
    return (
      <button
        disabled
        className="bg-zinc-800 text-zinc-400 px-6 py-3 rounded-lg"
      >
        Đang tải...
      </button>
    );
  }

  return (
    <button
      onClick={handleToggleWatchlist}
      disabled={loading}
      className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition duration-300 ${
        isInWatchlist
          ? "bg-green-600 hover:bg-green-700 text-white"
          : "bg-zinc-800 hover:bg-zinc-700 text-white"
      }`}
    >
      {isInWatchlist ? (
        <>
          <Check className="w-5 h-5" />
          <span>Đã lưu</span>
        </>
      ) : (
        <>
          <Bookmark className="w-5 h-5" />
          <span>Lưu vào danh sách</span>
        </>
      )}
    </button>
  );
};

export default WatchlistButton;
