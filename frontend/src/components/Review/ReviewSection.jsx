import { useEffect, useState } from "react";
import { reviewService } from "../../services/reviewService";
import ReviewForm from "./ReviewForm";
import ReviewList from "./ReviewList";
import RatingStars from "./RatingStars";
import { useAuth } from "../../hooks/useAuth";

const ReviewSection = ({ movieId }) => {
  const { user, isAuthenticated } = useAuth();
  const [reviews, setReviews] = useState([]);
  const [averageRating, setAverageRating] = useState(0);
  const [totalReviews, setTotalReviews] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [editingReview, setEditingReview] = useState(null);

  const fetchReviews = async () => {
    try {
      setLoading(true);

      const data = await reviewService.getMovieReviews(movieId);

      setReviews(data.items || []);

      setAverageRating(data.average_rating || 0);

      setTotalReviews(data.total_reviews || 0);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, [movieId]);

  const handleCreateReview = async (reviewData) => {
    try {
      setSubmitting(true);

      await reviewService.createReview(movieId, reviewData);

      await fetchReviews();
    } catch (error) {
      alert(error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdateReview = async (reviewData) => {
    try {
      setSubmitting(true);

      await reviewService.updateReview(editingReview.id, reviewData);

      setEditingReview(null);

      await fetchReviews();
    } catch (error) {
      alert(error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteReview = async (reviewId) => {
    const confirmed = window.confirm("Bạn chắc chắn muốn xóa đánh giá này?");

    if (!confirmed) return;

    try {
      await reviewService.deleteReview(reviewId);

      await fetchReviews();
    } catch (error) {
      alert(error);
    }
  };

  return (
    <section className="mt-20">
      <div className="flex items-center justify-between mb-10">
        <div>
          <h2 className="text-3xl font-bold">Đánh giá về bộ phim</h2>

          <p className="text-zinc-400 mt-2">{totalReviews} đánh giá</p>
        </div>

        <RatingStars rating={averageRating} />
      </div>

      {isAuthenticated ? (
        <ReviewForm
          onSubmit={editingReview ? handleUpdateReview : handleCreateReview}
          initialData={editingReview}
          loading={submitting}
        />
      ) : (
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-10 text-zinc-400">
          Đăng nhập để viết đánh giá
        </div>
      )}

      {loading ? (
        <div className="text-zinc-400">Đang tải các đánh giá...</div>
      ) : (
        <ReviewList
          reviews={reviews}
          currentUser={user}
          onEdit={setEditingReview}
          onDelete={handleDeleteReview}
        />
      )}
    </section>
  );
};

export default ReviewSection;
