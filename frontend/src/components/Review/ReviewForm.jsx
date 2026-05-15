import { useState, useEffect } from "react";
import RatingStars from "./RatingStars";

const ReviewForm = ({ onSubmit, initialData = null, loading = false }) => {
  const [rating, setRating] = useState(10);
  const [reviewText, setReviewText] = useState("");

  useEffect(() => {
    if (initialData) {
      setRating(initialData.rating);
      setReviewText(initialData.review_text || "");
    }
  }, [initialData]);

  const handleSubmit = (e) => {
    e.preventDefault();

    onSubmit({
      rating,
      review_text: reviewText,
    });

    if (!initialData) {
      setRating(10);
      setReviewText("");
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="
        bg-zinc-900/90
        backdrop-blur-sm
        border border-zinc-800
        rounded-3xl
        p-6 md:p-8
        mb-12
        shadow-2xl
      "
    >
      <div className="flex items-center justify-between gap-4 mb-8">
        <div>
          <h2 className="text-2xl md:text-3xl font-bold text-white">
            {initialData ? "Chỉnh sửa đánh giá" : "Tạo đánh giá"}
          </h2>
        </div>
      </div>

      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <label className="text-white font-semibold text-lg">Điểm</label>
        </div>

        <div
          className="
            bg-zinc-800/60
            border border-zinc-700
            rounded-2xl
            p-4
          "
        >
          <RatingStars rating={rating} onChange={setRating} interactive />
        </div>
      </div>

      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <label className="text-white font-semibold text-lg">Đánh giá</label>

          <span
            className={`text-sm ${
              reviewText.length > 1800 ? "text-yellow-400" : "text-zinc-500"
            }`}
          >
            {reviewText.length}/2000
          </span>
        </div>

        <textarea
          rows={6}
          value={reviewText}
          onChange={(e) => setReviewText(e.target.value)}
          placeholder="Chia sẻ những cảm nghĩ của bạn khi xem bộ phim"
          maxLength={2000}
          className="
            w-full
            bg-zinc-800/80
            border border-zinc-700
            rounded-2xl
            px-5 py-4
            text-white
            placeholder-zinc-500
            resize-none
            leading-7
            focus:outline-none
            focus:border-red-500
            focus:ring-2
            focus:ring-red-500/20
            transition-all
            duration-300
          "
        />
      </div>

      <div className="flex flex-col md:flex-row gap-4 md:items-center md:justify-between">
        <button
          type="submit"
          disabled={loading}
          className="
            bg-red-600
            hover:bg-red-700
            disabled:opacity-50
            disabled:cursor-not-allowed
            px-8 py-3.5
            rounded-2xl
            font-semibold
            text-white
            transition-all
            duration-300
            hover:scale-[1.02]
            shadow-lg
            shadow-red-600/20
          "
        >
          {loading
            ? "Submitting..."
            : initialData
              ? "Sửa đánh giá"
              : "Gửi đánh giá"}
        </button>
      </div>
    </form>
  );
};

export default ReviewForm;
