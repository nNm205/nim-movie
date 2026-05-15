import ReviewCard from "../Review/ReviewCard";

const UserReviewsSection = ({ reviews }) => {
  return (
    <section>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold">Đánh giá của bạn</h2>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 px-4 py-2 rounded-xl">
          <span className="text-zinc-400 text-sm">Tổng review:</span>

          <span className="ml-2 font-semibold text-white">
            {reviews.length}
          </span>
        </div>
      </div>

      {reviews.length === 0 ? (
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-12 text-center">
          <h3 className="text-2xl font-semibold text-white mb-3">
            Bạn chưa có review nào
          </h3>

          <p className="text-zinc-400">
            Hãy xem phim và chia sẻ cảm nhận của bạn
          </p>
        </div>
      ) : (
        <div className="space-y-5">
          {reviews.map((review) => (
            <ReviewCard
              key={review.id}
              review={review}
              currentUser={{
                id: review.user.id,
              }}
              showActions={false}
              showMovieLink={true}
            />
          ))}
        </div>
      )}
    </section>
  );
};

export default UserReviewsSection;
