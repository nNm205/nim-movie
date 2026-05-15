import { useState } from "react";
import { userService } from "../../services/userService";

const ProfileEditForm = ({ profile, onProfileUpdated }) => {
  const [username, setUsername] = useState(profile.username);
  const [email, setEmail] = useState(profile.email);

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);

      const updatedProfile = await userService.updateProfile({
        username,
        email,
      });

      onProfileUpdated(updatedProfile);

      alert("Profile updated successfully");
    } catch (error) {
      alert(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-8">
      <h2 className="text-2xl font-bold mb-8">Chỉnh sửa thông tin</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm text-zinc-400 mb-2">Username</label>

          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 focus:outline-none focus:border-red-500"
          />
        </div>

        <div>
          <label className="block text-sm text-zinc-400 mb-2">Email</label>

          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 focus:outline-none focus:border-red-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-red-600 hover:bg-red-700 disabled:opacity-50 px-6 py-3 rounded-xl font-semibold transition"
        >
          {loading ? "Đang lưu..." : "Lưu thay đổi"}
        </button>
      </form>
    </div>
  );
};

export default ProfileEditForm;
