import { MessageSquareText } from "lucide-react";
import ReviewCard from "./ReviewCard";

const ReviewList = ({ reviews, currentUser, onEdit, onDelete }) => {
  if (!reviews.length) {
    return (
      <div
        className="
          bg-zinc-900/80
          border border-zinc-800
          rounded-3xl
          py-20 px-6
          text-center
          shadow-xl
        "
      >
        <div
          className="
            w-20 h-20
            mx-auto
            mb-6
            rounded-2xl
            bg-zinc-800
            flex items-center justify-center
          "
        >
          <MessageSquareText className="w-10 h-10 text-zinc-500" />
        </div>

        <h3 className="text-2xl md:text-3xl font-bold text-white mb-4">
          Chưa có đánh giá về bộ phim
        </h3>

        <p className="text-zinc-400 text-base md:text-lg max-w-2xl mx-auto leading-7">
          Hãy là người đầu tiên chia sẻ cảm nghĩ của bạn về bộ phim sau khi xem
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {reviews.map((review) => (
        <ReviewCard
          key={review.id}
          review={review}
          currentUser={currentUser}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
};

export default ReviewList;
