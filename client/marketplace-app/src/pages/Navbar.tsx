import { useRef, useState } from "react";
import SVGComponent from "../components/SVGComponent";
import { Link } from "react-router-dom";
import { CircleX, MenuIcon } from "lucide-react";

const Navbar = () => {
  const closeTimeout = useRef<number | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const handleMouseEnter = () => {
    if (closeTimeout.current) {
      clearTimeout(closeTimeout.current);
      closeTimeout.current = null;
    }
    setIsOpen(true);
  };

  const handleMouseLeave = () => {
    closeTimeout.current = window.setTimeout(() => {
      setIsOpen(false);
      closeTimeout.current = null;
    }, 150); // 150ms 延遲，避免快速移動導致消失
  };
  return (
    <>
      <div className="relative flex flex-col items-center text-black pb-16 text-sm overflow-visible ">
        <div className="w-full py-2.5 font-medium text-sm text-white text-center bg-linear-to-r from-[#4F39F6] to-[#FDFEFF]">
          <p>
            <span className="px-3 py-1 rounded-md text-indigo-600 bg-white mr-2">
              官方公告:
            </span>
            預計 2025 年 12 月 31 日上線
          </p>
        </div>
        {/* 第一層 Nav */}
        <div className=" flex items-center justify-between p-4"></div>
        <div className="flex items-center border mx-4 w-full h-full max-w-4xl justify-between border-slate-700 px-4 py-2.5 rounded-full text-black overflow-visible">
          <div className="hidden md:block">
            <SVGComponent />
          </div>
          <div className="block md:hidden bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-full transition">
            前往贊助
          </div>
          <div className="flex-1 flex justify-center">
            <div className="max-md:absolute max-md:bg-black/50 max-md:backdrop-blur max-md:top-0 transition-all duration-300 max-md:h-full max-md:w-full max-md:z-10 max-md:-left-full max-md:justify-center flex-col md:flex-row flex items-center gap-2">
              <Link to="/" className="px-4 py-2">
                首頁
              </Link>

              <div
                className="relative"
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
              >
                <div className="flex items-center gap-1 hover:text-gray-300">
                  <span>市集</span>
                </div>
                {isOpen && (
                  <div className="absolute bg-white shadow-lg flex flex-col gap-2 w-max rounded-lg p-4 top-6 left-1/2 -translate-x-1/2 z-50 border">
                    <Link
                      to="/marketplace"
                      className="hover:translate-x-1 hover:text-slate-500 transition"
                    >
                      艾克瑟販售區
                    </Link>
                    <Link
                      to="/marketplace"
                      className="hover:translate-x-1 hover:text-slate-500 transition"
                    >
                      艾克瑟收購區
                    </Link>
                    <Link
                      to="/marketplace-sigrun"
                      className="hover:translate-x-1 hover:text-slate-500 transition"
                    >
                      西格倫販售區
                    </Link>
                    <Link
                      to="/marketplace"
                      className="hover:translate-x-1 hover:text-slate-500 transition"
                    >
                      西格倫收購區
                    </Link>
                    <Link
                      to="/marketplace"
                      className="hover:translate-x-1 hover:text-slate-500 transition"
                    >
                      波利販賣區
                    </Link>
                    <Link
                      to="/marketplace"
                      className="hover:translate-x-1 hover:text-slate-500 transition"
                    >
                      波利收購區
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="hidden md:block bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-full transition">
            Login
          </div>
          {/* 中間路由選單 */}

          <div>
            <MenuIcon
              onClick={() => setMenuOpen(true)}
              size={24}
              // color="white"
              className="block md:hidden"
            />
          </div>
        </div>
      </div>
      {/* Mobile Menu */}
      <div
        className={`fixed inset-0  bg-black/40 text-black backdrop-blur flex flex-col items-center justify-center text-lg gap-8 md:hidden transition-transform duration-300 ${
          menuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <Link to="/" className="text-white" onClick={() => setMenuOpen(false)}>
          首頁
        </Link>
        <Link to="/marketplace" className="text-white">
          市集
        </Link>
        <div className=" bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-full transition">
          Login
        </div>
        <CircleX
          onClick={() => setMenuOpen(false)}
          className="absolute size-8 right-6 top-6 cursor-pointer text-teal-50 hover:text-red-500"
        />
        <div className="active:ring-3 active:ring-white aspect-square size-10 p-1 items-center justify-center  transition text-white rounded-md flex"></div>
      </div>
    </>
  );
};

export default Navbar;
