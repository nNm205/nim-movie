const UsernameInput = ({ value, onChange }) => {
  return (
    <div>
      <label className="block text-sm font-medium text-zinc-300 mb-2">
        Username
      </label>
      <div className="relative">
        <input
          type="text"
          placeholder="Nhập username"
          value={value}
          onChange={onChange}
          className="w-full pl-4 pr-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-red-500 focus:ring-2 focus:ring-red-500/20 transition-all"
          required
        />
      </div>
    </div>
  );
};

export default UsernameInput;
