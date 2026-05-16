import { useEffect, useRef, useState } from "react";
import { ChevronDown, Check } from "lucide-react";

const FilterDropdown = ({
  label,
  options = [],
  value,
  onChange,
  width = "w-64",
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const selectedOption =
    options.find((option) => String(option.value) === String(value)) ||
    options[0];

  return (
    <div ref={dropdownRef} className={`relative ${width}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="
          w-full
          flex
          items-center
          justify-between
          px-5
          py-3
          rounded-xl
          bg-zinc-900/90
          border
          border-zinc-700
          hover:border-red-500
          text-white
          transition-all
          duration-200
        "
      >
        <div className="flex flex-col items-start">
          <span className="text-xs text-zinc-400">{label}</span>

          <span className="font-medium">{selectedOption?.label}</span>
        </div>

        <ChevronDown
          className={`w-5 h-5 text-zinc-400 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {isOpen && (
        <div
          className="
            absolute
            top-full
            left-0
            mt-3
            w-full
            rounded-2xl
            border
            border-zinc-800
            bg-zinc-900
            shadow-2xl
            shadow-black/50
            overflow-hidden
            z-50
          "
        >
          <div
            className="
              max-h-72
              overflow-y-auto
              scrollbar-hide
            "
          >
            {options.map((option) => {
              const isSelected = String(option.value) === String(value);

              return (
                <button
                  key={option.value}
                  onClick={() => {
                    onChange(option.value);
                    setIsOpen(false);
                  }}
                  className={`
                    w-full
                    flex
                    items-center
                    justify-between
                    px-5
                    py-3
                    text-left
                    transition
                    ${
                      isSelected
                        ? "bg-red-500/10 text-red-400"
                        : "text-zinc-300 hover:bg-zinc-800 hover:text-white"
                    }
                  `}
                >
                  <span>{option.label}</span>

                  {isSelected && <Check className="w-4 h-4" />}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterDropdown;
