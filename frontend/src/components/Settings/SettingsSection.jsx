const SettingsSection = ({ title, description, children }) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white">{title}</h2>

        {description && <p className="text-zinc-400 mt-2">{description}</p>}
      </div>

      {children}
    </div>
  );
};

export default SettingsSection;
