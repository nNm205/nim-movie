import RatingStars from "./RatingStars";

const ReviewCard = ({ review, currentUser, onEdit, onDelete }) => {
  const isOwner = currentUser?.id === review.user?.id;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-white">{review.user?.username}</h3>

          <p className="text-sm text-zinc-500">
            {new Date(review.created_at).toLocaleDateString()}
          </p>
        </div>

        <RatingStars rating={review.rating} />
      </div>

      <p className="text-zinc-300 leading-7">{review.review_text}</p>

      {isOwner && (
        <div className="flex gap-3 mt-5">
          <button
            onClick={() => onEdit(review)}
            className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm transition"
          >
            Sửa
          </button>

          <button
            onClick={() => onDelete(review.id)}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm transition"
          >
            Xóa
          </button>
        </div>
      )}
    </div>
  );
};

export default ReviewCard;
