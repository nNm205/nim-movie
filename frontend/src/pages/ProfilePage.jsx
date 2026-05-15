import { useEffect, useState } from "react";
import Layout from "../components/Common/Layout";
import { userService } from "../services/userService";
import { reviewService } from "../services/reviewService";
import ProfileHeader from "../components/Profile/ProfileHeader";
import ProfileEditForm from "../components/Profile/ProfileEditForm";
import UserReviewsSection from "../components/Profile/UserReviewsSection";

const ProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const data = await userService.getProfile();

      setProfile(data);
    } catch (error) {
      console.error(error);
    }
  };

  const fetchReviews = async () => {
    try {
      const data = await reviewService.getMyReviews();

      setReviews(data.items || []);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);

        await Promise.all([fetchProfile(), fetchReviews()]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleProfileUpdated = (updatedProfile) => {
    setProfile(updatedProfile);
  };

  if (loading) {
    return (
      <Layout>
        <div className="text-white text-center py-20">
          Đang tải thông tin...
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="bg-black text-white min-h-screen">
        <div className="max-w-6xl mx-auto px-4 py-10">
          <ProfileHeader profile={profile} />

          <div className="mt-10">
            <ProfileEditForm
              profile={profile}
              onProfileUpdated={handleProfileUpdated}
            />
          </div>

          <div className="mt-16">
            <UserReviewsSection reviews={reviews} />
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ProfilePage;
