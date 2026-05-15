import { createContext, useContext, useEffect, useState } from "react";

const SettingsContext = createContext();

export const SettingsProvider = ({ children }) => {
  const [theme, setTheme] = useState("dark");
  const [language, setLanguage] = useState("vi");
  const [autoplayTrailer, setAutoplayTrailer] = useState(true);
  const [blurBackdrop, setBlurBackdrop] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("nimmovie-settings");

    if (saved) {
      const parsed = JSON.parse(saved);

      setTheme(parsed.theme || "dark");
      setLanguage(parsed.language || "vi");
      setAutoplayTrailer(parsed.autoplayTrailer ?? true);
      setBlurBackdrop(parsed.blurBackdrop ?? true);
      setEmailNotifications(parsed.emailNotifications ?? false);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(
      "nimmovie-settings",
      JSON.stringify({
        theme,
        language,
        autoplayTrailer,
        blurBackdrop,
        emailNotifications,
      }),
    );
  }, [theme, language, autoplayTrailer, blurBackdrop, emailNotifications]);

  return (
    <SettingsContext.Provider
      value={{
        theme,
        setTheme,

        language,
        setLanguage,

        autoplayTrailer,
        setAutoplayTrailer,

        blurBackdrop,
        setBlurBackdrop,

        emailNotifications,
        setEmailNotifications,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => useContext(SettingsContext);
