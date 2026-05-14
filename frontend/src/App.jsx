import { Route, Routes } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import Header from "./components/Common/Header";
import Footer from "./components/Common/Footer";

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-zinc-950 overflow-hidden">
      <Header />
      <main className="pt-24 pb-96 min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
