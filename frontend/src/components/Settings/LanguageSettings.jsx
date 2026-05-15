import { useState, useRef, useEffect } from "react";
import SettingsSection from "./SettingsSection";
import { useSettings } from "../../context/SettingsContext";

const LanguageSettings = () => {
  const { language, setLanguage } = useSettings();
  const [open, setOpen] = useState(false);
  const ref = useRef();

  const options = [
    { value: "vi", label: "Vietnamese" },
    { value: "en", label: "English" },
  ];

  const current = options.find((o) => o.value === language);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <SettingsSection title="Ngôn ngữ">
      <div ref={ref} className="relative w-full">
        <button
          onClick={() => setOpen(!open)}
          className="
            w-full flex justify-between items-center
            bg-zinc-800 border border-zinc-700
            rounded-xl px-4 py-3
            text-white
            transition-all duration-200
            hover:border-zinc-500
          "
        >
          <span>{current?.label}</span>
          <span
            className={`transition-transform duration-200 ${
              open ? "rotate-180" : ""
            }`}
          >
            ▼
          </span>
        </button>

        <div
          className={`
            absolute z-50 mt-2 w-full
            bg-zinc-900 border border-zinc-700
            rounded-xl overflow-hidden
            shadow-xl
            transition-all duration-200 origin-top
            ${
              open
                ? "opacity-100 scale-100"
                : "opacity-0 scale-95 pointer-events-none"
            }
          `}
        >
          {options.map((opt) => (
            <div
              key={opt.value}
              onClick={() => {
                setLanguage(opt.value);
                setOpen(false);
              }}
              className="
                px-4 py-3 cursor-pointer
                text-white
                hover:bg-zinc-800
                transition
              "
            >
              {opt.label}
            </div>
          ))}
        </div>
      </div>
    </SettingsSection>
  );
};

export default LanguageSettings;
