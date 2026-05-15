import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./index.css";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import { MovieProvider } from "./context/MovieContext.jsx";
import { SettingsProvider } from "./context/SettingsContext.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <MovieProvider>
          <SettingsProvider>
            <App />
          </SettingsProvider>
        </MovieProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
