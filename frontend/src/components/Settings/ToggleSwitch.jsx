const ToggleSwitch = ({ enabled, onChange }) => {
  return (
    <button
      onClick={() => onChange(!enabled)}
      className={`relative w-14 h-8 rounded-full transition duration-300 ${
        enabled ? "bg-red-600" : "bg-zinc-700"
      }`}
    >
      <div
        className={`absolute top-1 w-6 h-6 bg-white rounded-full transition duration-300 ${
          enabled ? "left-7" : "left-1"
        }`}
      />
    </button>
  );
};

export default ToggleSwitch;
