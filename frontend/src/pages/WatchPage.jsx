import { useParams, useNavigate } from "react-router-dom";

import { FiArrowLeft } from "react-icons/fi";

const WatchPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div className="w-full h-screen bg-black flex items-center justify-center relative">
      <button
        onClick={() => navigate(-1)}
        className="absolute top-5 left-5 z-50 flex items-center gap-2 bg-black/60 hover:bg-red-600 text-white p-3 rounded transition"
      >
        <FiArrowLeft size={22} />
      </button>

      <div className="text-center">
        <h1 className="text-white text-5xl font-bold mb-5">Movie Player</h1>

        <p className="text-gray-400 text-lg">
          Streaming feature chưa được triển khai
        </p>

        <p className="text-gray-500 mt-3">Movie ID: {id}</p>
      </div>
    </div>
  );
};

export default WatchPage;
