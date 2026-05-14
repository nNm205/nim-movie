const AuthHeader = ({ title, subtitle }) => {
  return (
    <div className="text-center mb-8">
      <div className="flex items-center justify-center gap-2 mb-4">
        <span className="text-3xl font-black tracking-tight">
          <span className="bg-gradient-to-r from-red-500 via-red-400 to-orange-500 bg-clip-text text-transparent">
            Nim
          </span>
          <span className="text-white">Movie</span>
        </span>
      </div>
      <h1 className="text-2xl font-bold text-white mb-2">{title}</h1>
      <p className="text-zinc-400">{subtitle}</p>
    </div>
  );
};

export default AuthHeader;
