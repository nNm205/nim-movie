import { Star } from "lucide-react";

const RatingStars = ({ rating = 0, onChange, interactive = false }) => {
  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((star) => (
        <button
          key={star}
          type="button"
          disabled={!interactive}
          onClick={() => interactive && onChange(star)}
          className={`transition transform ${
            interactive ? "hover:scale-125 cursor-pointer" : ""
          }`}
        >
          <Star
            className={`w-6 h-6 ${
              star <= rating
                ? "fill-yellow-400 text-yellow-400"
                : "text-zinc-600"
            }`}
          />
        </button>
      ))}

      <span className="ml-2 text-sm text-zinc-400">{rating}/10</span>
    </div>
  );
};

export default RatingStars;
