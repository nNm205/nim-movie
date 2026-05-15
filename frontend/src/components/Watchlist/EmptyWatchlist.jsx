import { Link } from "react-router-dom";
import { BookmarkX } from "lucide-react";

const EmptyWatchlist = () => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-3xl py-20 px-6 text-center">
      <div className="flex justify-center mb-6">
        <div className="bg-zinc-800 p-6 rounded-full">
          <BookmarkX className="w-14 h-14 text-zinc-500" />
        </div>
      </div>

      <h2 className="text-3xl font-bold text-white mb-4">
        Danh sách xem sau của bạn đang trống
      </h2>

      <p className="text-zinc-400 max-w-xl mx-auto leading-7 mb-8">
        Lưu những bộ phim bạn yêu thích để xem lại dễ dàng hơn sau này.
      </p>

      <Link
        to="/"
        className="inline-flex items-center justify-center bg-red-600 hover:bg-red-700 text-white px-8 py-4 rounded-xl font-semibold transition"
      >
        Khám phá các bộ phim hay
      </Link>
    </div>
  );
};

export default EmptyWatchlist;
