import { User } from "lucide-react";

const ProfileHeader = ({ profile }) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-8">
      <div className="flex items-center gap-6">
        <div className="w-24 h-24 rounded-full bg-red-600 flex items-center justify-center">
          <User className="w-12 h-12 text-white" />
        </div>

        <div>
          <h1 className="text-4xl font-bold">{profile.username}</h1>

          <p className="text-zinc-400 mt-2">{profile.email}</p>

          <div className="mt-4 inline-block bg-red-600/20 text-red-400 px-4 py-2 rounded-full text-sm">
            {profile.role}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileHeader;
