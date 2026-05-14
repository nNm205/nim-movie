import { Link } from "react-router-dom";
import { Mail, Phone, MapPin } from "lucide-react";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gradient-to-r from-zinc-950 via-zinc-900 to-zinc-950 border-t border-zinc-800/50">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div className="space-y-4">
            <Link to="/" className="flex items-center space-x-2 group w-fit">
              <span className="text-2xl font-black tracking-tight">
                <span className="bg-gradient-to-r from-red-500 via-red-400 to-orange-500 bg-clip-text text-transparent">
                  Nim
                </span>
                <span className="text-white">Movie</span>
              </span>
            </Link>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Nền tảng xem phim trực tuyến hàng đầu với hàng ngàn bộ phim chất
              lượng cao, phụ đề tiếng Việt và trải nghiệm xem phim tuyệt vời.
            </p>
          </div>

          <div>
            <h3 className="text-white font-semibold text-lg mb-4">
              Liên kết nhanh
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  to="/"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200 text-sm flex items-center group"
                >
                  <span className="w-0 group-hover:w-2 h-0.5 bg-red-500 mr-0 group-hover:mr-2 transition-all duration-200"></span>
                  Trang chủ
                </Link>
              </li>
              <li>
                <Link
                  to="/movies"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200 text-sm flex items-center group"
                >
                  <span className="w-0 group-hover:w-2 h-0.5 bg-red-500 mr-0 group-hover:mr-2 transition-all duration-200"></span>
                  Danh sách phim
                </Link>
              </li>
              <li>
                <Link
                  to="/trending"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200 text-sm flex items-center group"
                >
                  <span className="w-0 group-hover:w-2 h-0.5 bg-red-500 mr-0 group-hover:mr-2 transition-all duration-200"></span>
                  Xu hướng
                </Link>
              </li>
              <li>
                <Link
                  to="/new"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200 text-sm flex items-center group"
                >
                  <span className="w-0 group-hover:w-2 h-0.5 bg-red-500 mr-0 group-hover:mr-2 transition-all duration-200"></span>
                  Phim mới
                </Link>
              </li>
              <li>
                <Link
                  to="/category"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200 text-sm flex items-center group"
                >
                  <span className="w-0 group-hover:w-2 h-0.5 bg-red-500 mr-0 group-hover:mr-2 transition-all duration-200"></span>
                  Thể loại
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-white font-semibold text-lg mb-4">Hỗ trợ</h3>
            <ul className="space-y-3">
              <li>
                <Link
                  to="/about"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200 text-sm flex items-center group"
                >
                  <span className="w-0 group-hover:w-2 h-0.5 bg-red-500 mr-0 group-hover:mr-2 transition-all duration-200"></span>
                  Về chúng tôi
                </Link>
              </li>
              <li>
                <Link
                  to="/contact"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200 text-sm flex items-center group"
                >
                  <span className="w-0 group-hover:w-2 h-0.5 bg-red-500 mr-0 group-hover:mr-2 transition-all duration-200"></span>
                  Liên hệ
                </Link>
              </li>
              <li>
                <Link
                  to="/faq"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200 text-sm flex items-center group"
                >
                  <span className="w-0 group-hover:w-2 h-0.5 bg-red-500 mr-0 group-hover:mr-2 transition-all duration-200"></span>
                  Câu hỏi thường gặp
                </Link>
              </li>
              <li>
                <Link
                  to="/privacy"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200 text-sm flex items-center group"
                >
                  <span className="w-0 group-hover:w-2 h-0.5 bg-red-500 mr-0 group-hover:mr-2 transition-all duration-200"></span>
                  Chính sách bảo mật
                </Link>
              </li>
              <li>
                <Link
                  to="/terms"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200 text-sm flex items-center group"
                >
                  <span className="w-0 group-hover:w-2 h-0.5 bg-red-500 mr-0 group-hover:mr-2 transition-all duration-200"></span>
                  Điều khoản sử dụng
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-white font-semibold text-lg mb-4">Liên hệ</h3>
            <ul className="space-y-4">
              <li className="flex items-start space-x-3 text-sm">
                <MapPin className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <span className="text-zinc-400">TP. Hà Nội, Việt Nam</span>
              </li>
              <li className="flex items-center space-x-3 text-sm">
                <Phone className="w-5 h-5 text-red-500 flex-shrink-0" />
                <a
                  href="tel:+84123456789"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200"
                >
                  +84 12 345 6789
                </a>
              </li>
              <li className="flex items-center space-x-3 text-sm">
                <Mail className="w-5 h-5 text-red-500 flex-shrink-0" />
                <a
                  href="mailto:support@nimmovie.com"
                  className="text-zinc-400 hover:text-red-500 transition-colors duration-200"
                >
                  support@nimmovie.com
                </a>
              </li>
            </ul>

            <div className="mt-6">
              <p className="text-zinc-400 text-sm mb-3">Đăng ký nhận tin mới</p>
              <form className="flex space-x-2">
                <input
                  type="email"
                  placeholder="Email của bạn"
                  className="flex-1 px-3 py-2 rounded-lg bg-zinc-800/50 border border-zinc-700 text-white text-sm placeholder-zinc-500 focus:outline-none focus:border-red-500 focus:ring-2 focus:ring-red-500/20 transition-all"
                />
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-gradient-to-r from-red-600 to-red-500 text-white font-medium hover:from-red-500 hover:to-red-400 transition-all duration-300 shadow-lg shadow-red-500/30 hover:shadow-red-500/50 text-sm"
                >
                  Gửi
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-zinc-800/50 bg-zinc-950/50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-row justify-center space-y-3 md:space-y-0">
            <p className="text-zinc-500 text-sm text-center">
              © {currentYear} NimMovie. Bản quyền thuộc về chúng tôi.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
