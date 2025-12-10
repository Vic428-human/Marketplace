import React, { useRef, useState } from "react";
import SVGComponent from "../components/SVGComponent";

const Navbar = () => {
  const closeTimeout = useRef<number | null>(null);
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
      <div className="flex items-center border mx-4 w-full max-w-4xl justify-between border-slate-700 px-4 py-2.5 rounded-full text-white">
        <SVGComponent />

        <div className="flex-1 flex justify-center">
          <div
            id="menu"
            className="max-md:absolute max-md:bg-black/50 max-md:backdrop-blur max-md:top-0 transition-all duration-300 max-md:h-full max-md:w-full max-md:z-10 max-md:-left-full max-md:justify-center flex-col md:flex-row flex items-center gap-2"
          >
            <div className="px-4 py-2">首頁</div>

            <div
              className="relative"
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            >
              <div className="flex items-center gap-1 hover:text-gray-300">
                <span>市集</span>
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path
                    d="m4.5 7.2 3.793 3.793a1 1 0 0 0 1.414 0L13.5 7.2"
                    stroke="white"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>

              {isOpen && (
                <div className="absolute bg-slate-900 font-normal flex flex-col gap-2 w-max rounded-lg p-4 top-10 left-1/2 -translate-x-1/2">
                  <a
                    href="/marketplace"
                    className="hover:translate-x-1 hover:text-slate-500 transition"
                  >
                    買賣刊登資訊
                  </a>
                </div>
              )}
            </div>

            <div className="px-4 py-2">測試1</div>

            <div className="px-4 py-2">測試2</div>

            <div className="px-4 py-2">測試3</div>
          </div>
        </div>
        {/* 中間路由選單 */}
        <button className="hidden md:block bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-full transition">
          前往贊助
        </button>
        <button className="block md:hidden bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-full transition">
          手機模式註冊!!
        </button>
      </div>
    </>
  );
};

export default Navbar;
