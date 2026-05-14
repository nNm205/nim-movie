import { Link, useNavigate } from "react-router-dom";
import { User, Search, Menu, X, LogOut, Settings } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { useAuth } from "../../hooks/useAuth";

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const searchRef = useRef(null);
  const userMenuRef = useRef(null);
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsSearchOpen(false);
      }

      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setIsUserMenuOpen(false);
      }
    };

    if (isSearchOpen || isUserMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isSearchOpen, isUserMenuOpen]);

  const handleSearch = (e) => {
    e.preventDefault();
    console.log("Search: ", searchQuery);
  };

  const handleLogout = () => {
    logout();
    setIsUserMenuOpen(false);
    navigate("/");
  };

  return (
    <header className="bg-gradient-to-r from-zinc-950 via-zinc-900 to-zinc-950 border-b border-zinc-800/50 backdrop-blur-sm sticky top-0 z-50 shadow-lg shadow-black/20">
      <div className="container mx-auto px-4 h-20 flex items-center justify-between">
        <Link
          to="/"
          className="flex items-center space-x-2 group flex-shrink-0"
        >
          <span className="text-2xl font-black tracking-tight">
            <span className="bg-gradient-to-r from-red-500 via-red-400 to-orange-500 bg-clip-text text-transparent">
              Nim
            </span>
            <span className="text-white">Movie</span>
          </span>
        </Link>

        <nav className="hidden md:flex items-center space-x-1">
          <Link
            to="/"
            className="px-4 py-2 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium"
          >
            Trang chủ
          </Link>
          <Link
            to="/movies"
            className="px-4 py-2 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium"
          >
            Danh sách phim
          </Link>
          <Link
            to="/trending"
            className="px-4 py-2 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium"
          >
            Xu hướng
          </Link>
          <Link
            to="/new"
            className="px-4 py-2 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium"
          >
            Phim mới
          </Link>
          <Link
            to="/category"
            className="px-4 py-2 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium"
          >
            Thể loại
          </Link>
        </nav>

        <div className="hidden md:flex items-center space-x-3">
          <div ref={searchRef} className="relative">
            <div
              className={`flex items-center transition-all duration-300 ${
                isSearchOpen ? "w-64" : "w-10"
              }`}
            >
              {isSearchOpen ? (
                <form onSubmit={handleSearch} className="w-full">
                  <div className="relative">
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Tìm kiếm phim..."
                      className="w-full px-4 py-2.5 pr-10 rounded-lg bg-zinc-800/50 border border-zinc-700 text-white placeholder-zinc-400 focus:outline-none focus:border-red-500 focus:ring-2 focus:ring-red-500/20 transition-all"
                      autoFocus
                    />
                    <button
                      type="submit"
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-zinc-400 hover:text-white transition-colors"
                    >
                      <Search className="w-4 h-4" />
                    </button>
                  </div>
                </form>
              ) : (
                <button
                  onClick={() => setIsSearchOpen(true)}
                  className="p-2.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800/50 transition-all duration-200"
                >
                  <Search className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>

          {isAuthenticated ? (
            <div ref={userMenuRef} className="relative">
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-zinc-800/50 transition-all duration-200"
              >
                {user.avatar ? (
                  <img
                    src={user.avatar}
                    alt={user.username}
                    className="w-9 h-9 rounded-full object-cover border-2 border-zinc-700 hover:border-red-500 transition-colors"
                  />
                ) : (
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-red-600 to-red-500 flex items-center justify-center border-2 border-zinc-700 hover:border-red-500 transition-colors">
                    <User className="w-5 h-5 text-white" />
                  </div>
                )}
              </button>

              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-zinc-900 border border-zinc-800 rounded-xl shadow-2xl shadow-black/50 overflow-hidden">
                  <div className="p-4 border-b border-zinc-800 bg-zinc-800/50">
                    <div className="flex items-center gap-3">
                      {user.avatar ? (
                        <img
                          src={user.avatar}
                          alt={user.username}
                          className="w-12 h-12 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-red-600 to-red-500 flex items-center justify-center">
                          <User className="w-6 h-6 text-white" />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-white font-semibold truncate">
                          {user.username}
                        </p>
                        <p className="text-zinc-400 text-sm truncate">
                          {user.email}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="py-2">
                    <Link
                      to="/profile"
                      onClick={() => setIsUserMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-3 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-all"
                    >
                      <User className="w-5 h-5" />
                      <span>Trang cá nhân</span>
                    </Link>

                    <Link
                      to="/settings"
                      onClick={() => setIsUserMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-3 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-all"
                    >
                      <Settings className="w-5 h-5" />
                      <span>Cài đặt</span>
                    </Link>

                    <div className="border-t border-zinc-800 my-2"></div>

                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-3 text-red-400 hover:text-red-300 hover:bg-zinc-800 transition-all"
                    >
                      <LogOut className="w-5 h-5" />
                      <span>Đăng xuất</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <>
              <Link
                to="/login"
                className="px-4 py-2.5 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium flex items-center space-x-2"
              >
                <span>Đăng nhập</span>
              </Link>

              <Link
                to="/register"
                className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-red-600 to-red-500 text-white font-semibold hover:from-red-500 hover:to-red-400 transition-all duration-300 shadow-lg shadow-red-500/30 hover:shadow-red-500/50 hover:scale-105"
              >
                Đăng ký
              </Link>
            </>
          )}
        </div>

        <div className="md:hidden flex items-center space-x-2">
          <button
            onClick={() => setIsSearchOpen(!isSearchOpen)}
            className="p-2 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800/50 transition-all duration-200"
          >
            {isSearchOpen ? (
              <X className="w-5 h-5" />
            ) : (
              <Search className="w-5 h-5" />
            )}
          </button>

          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="p-2 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800/50 transition-all duration-200"
          >
            {isMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>
      </div>

      <div
        className={`md:hidden overflow-hidden transition-all duration-300 ${
          isSearchOpen ? "max-h-20 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div ref={searchRef} className="container mx-auto px-4 pb-4">
          <form onSubmit={handleSearch}>
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm kiếm phim..."
                className="w-full px-4 py-3 pr-12 rounded-lg bg-zinc-800/50 border border-zinc-700 text-white placeholder-zinc-400 focus:outline-none focus:border-red-500 focus:ring-2 focus:ring-red-500/20 transition-all"
              />
              <button
                type="submit"
                className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-zinc-400 hover:text-white transition-colors"
              >
                <Search className="w-5 h-5" />
              </button>
            </div>
          </form>
        </div>
      </div>

      <div
        className={`md:hidden overflow-hidden transition-all duration-300 ${
          isMenuOpen ? "max-h-[500px] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="bg-zinc-900/95 backdrop-blur-sm border-t border-zinc-800/50">
          <nav className="container mx-auto px-4 py-4 flex flex-col space-y-2">
            <Link
              to="/"
              onClick={() => setIsMenuOpen(false)}
              className="px-4 py-3 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium"
            >
              Trang chủ
            </Link>
            <Link
              to="/movies"
              onClick={() => setIsMenuOpen(false)}
              className="px-4 py-3 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium"
            >
              Danh sách phim
            </Link>
            <Link
              to="/trending"
              onClick={() => setIsMenuOpen(false)}
              className="px-4 py-3 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium"
            >
              Xu hướng
            </Link>
            <Link
              to="/new"
              onClick={() => setIsMenuOpen(false)}
              className="px-4 py-3 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium"
            >
              Phim mới
            </Link>
            <Link
              to="/category"
              onClick={() => setIsMenuOpen(false)}
              className="px-4 py-3 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium"
            >
              Thể loại
            </Link>

            <div className="pt-2 border-t border-zinc-800">
              {isAuthenticated ? (
                <>
                  <div className="px-4 py-3 flex items-center gap-3">
                    {user.avatar ? (
                      <img
                        src={user.avatar}
                        alt={user.username}
                        className="w-10 h-10 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-600 to-red-500 flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-white font-semibold truncate">
                        {user.username}
                      </p>
                      <p className="text-zinc-400 text-sm truncate">
                        {user.email}
                      </p>
                    </div>
                  </div>

                  <Link
                    to="/profile"
                    onClick={() => setIsMenuOpen(false)}
                    className="px-4 py-3 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium flex items-center gap-2"
                  >
                    <User className="w-5 h-5" />
                    <span>Trang cá nhân</span>
                  </Link>

                  <Link
                    to="/settings"
                    onClick={() => setIsMenuOpen(false)}
                    className="px-4 py-3 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium flex items-center gap-2"
                  >
                    <Settings className="w-5 h-5" />
                    <span>Cài đặt</span>
                  </Link>

                  <button
                    onClick={() => {
                      handleLogout();
                      setIsMenuOpen(false);
                    }}
                    className="w-full px-4 py-3 rounded-lg text-red-400 hover:text-red-300 hover:bg-zinc-800/50 transition-all duration-200 font-medium flex items-center gap-2"
                  >
                    <LogOut className="w-5 h-5" />
                    <span>Đăng xuất</span>
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    onClick={() => setIsMenuOpen(false)}
                    className="px-4 py-3 rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/50 transition-all duration-200 font-medium"
                  >
                    Đăng nhập
                  </Link>
                  <Link
                    to="/register"
                    onClick={() => setIsMenuOpen(false)}
                    className="px-4 py-3 rounded-lg bg-gradient-to-r from-red-600 to-red-500 text-white font-semibold hover:from-red-500 hover:to-red-400 transition-all duration-300 text-center"
                  >
                    Đăng ký
                  </Link>
                </>
              )}
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
