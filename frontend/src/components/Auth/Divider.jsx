const Divider = ({ text = "Hoặc" }) => {
  return (
    <div className="relative my-6">
      <div className="absolute inset-0 flex items-center">
        <div className="w-full border-t border-zinc-700"></div>
      </div>
      <div className="relative flex justify-center text-sm">
        <span className="px-4 bg-zinc-900 text-zinc-500">{text}</span>
      </div>
    </div>
  );
};

export default Divider;
