import React, { useState, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Navbar from "../pages/Navbar";

export default function Hero() {
  const [input, setInput] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const { pathname } = useLocation();

  const navigate = useNavigate();

  const onSubmitHandler = (e: { preventDefault: () => void }) => {
    e.preventDefault();
    navigate(`/marketplace?search=${input}`);
  };

  // https://prebuiltui.com/components/hero-section#hero-section-with-banner-84fb
  //  參考上面版型

  return (
    <>
      <section className="flex flex-col items-center bg-gradient-to-b from-black to-[#1A0033] text-white pb-16 text-sm overflow-hidden relative">
        <div className="w-full py-2.5 font-medium text-sm text-white text-center bg-gradient-to-r from-[#4F39F6] to-[#FDFEFF]">
          <p>
            <span className="px-3 py-1 rounded-md text-indigo-600 bg-white mr-2">
              官方公告:
            </span>
            預計 2025 年 12 月 31 日上線
          </p>
        </div>
        {/* 第一層 Nav */}
        <nav className="flex items-center justify-between p-4 md:px-16 lg:px-24 xl:px-32 md:py-6 w-full z-50">
          <a href="https://prebuiltui.com"></a>

          {/* 電腦模式註冊*/}
          <div className="hidden md:block bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-full transition">
            電腦模式註冊
          </div>

          {/* 手機模式會出現漢堡選單 */}
          <div
            onClick={() => setMenuOpen(true)}
            className="md:hidden active:scale-90 transition"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="26"
              height="26"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="lucide lucide-menu"
            >
              <path d="M4 5h16M4 12h16M4 19h16" />
            </svg>
          </div>
        </nav>
        {/* Mobile Menu */}
        <div
          className={`fixed inset-0 z-[100] bg-black/40 text-black backdrop-blur flex flex-col items-center justify-center text-lg gap-8 md:hidden transition-transform duration-300 ${
            menuOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <a href="/" className="text-white">
            首頁
          </a>
          <a href="/marketplace" className="text-white">
            市集
          </a>
          <button
            onClick={() => setMenuOpen(false)}
            className="active:ring-3 active:ring-white aspect-square size-10 p-1 items-center justify-center bg-indigo-600 hover:bg-indigo-700 transition text-white rounded-md flex"
          >
            X
          </button>
        </div>
        {/* 第二層 Nav */}
        {!pathname.includes("/admin") && <Navbar />}

        <div className="flex flex-wrap items-center justify-center p-1.5 mt-32 rounded-full border border-indigo-900 text-xs">
          <div className="flex items-center -space-x-3">
            <img
              className="rounded-full border-3 border-white"
              src="https://images.unsplash.com/photo-1633332755192-727a05c4013d?q=80&w=50"
              alt="user"
            />
          </div>
          <p className="ml-4">XX user 刊登了 xx 道具</p>
        </div>

        <h1 className="text-4xl md:text-6xl text-center font-medium max-w-3xl mt-5 bg-gradient-to-r from-white to-[#748298] text-transparent bg-clip-text">
          Mbao.com
        </h1>

        <p className="text-slate-100 md:text-base text-center max-w-xl mt-3 max-md:px-4">
          平均 47 秒就有人出價，你還在等什麼？
        </p>

        {/* 搜尋特定物品導引去 marketplace  */}
        <form
          onSubmit={onSubmitHandler}
          className="w-full flex justify-center group"
        >
          <label className="border border-gray-400 rounded-md p-1 flex items-center w-fㄋull max-w-md">
            <input
              onChange={(e) => setInput(e.target.value)}
              value={input}
              type="text"
              placeholder="輸入虛寶關鍵字..."
              className="pl-2 flex-1 outline-none"
            />
            <div className="bg-indigo-600 text-white p-3 px-6 rounded-md cursor-pointer">
              查詢
            </div>
          </label>
        </form>
      </section>
    </>
  );
}
