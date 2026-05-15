import { Route, Routes, Navigate } from "react-router-dom";
import PrivateRoute from "./components/Auth/PrivateRoute";

import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import HomePage from "./pages/HomePage";
import MovieDetailPage from "./pages/MovieDetailPage";
import WatchPage from "./pages/WatchPage";
import SearchResultPage from "./pages/SearchResultsPage";
import ProfilePage from "./pages/ProfilePage";

function App() {
  return (
    <div className="min-h-screen bg-zinc-950">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/search" element={<SearchResultPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <HomePage />
            </PrivateRoute>
          }
        />
        <Route
          path="/movies/:id"
          element={
            <PrivateRoute>
              <MovieDetailPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/watch/:id"
          element={
            <PrivateRoute>
              <WatchPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <PrivateRoute>
              <ProfilePage />
            </PrivateRoute>
          }
        />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  );
}

export default App;
