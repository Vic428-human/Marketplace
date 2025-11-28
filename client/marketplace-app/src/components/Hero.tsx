import React, { useState, useRef } from "react";

export default function HeroSection() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  const [isOpen, setIsOpen] = useState(false);
  const closeTimeout = useRef<number | null>(null);

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

  const handleCopy = async () => {
    await navigator.clipboard.writeText("npx prisma@latest init --db");
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 3000);
  };

  // https://prebuiltui.com/components/hero-section#hero-section-with-banner-84fb
  //  參考上面版型

  return (
    <>
      <section className="flex flex-col items-center bg-gradient-to-b from-black to-[#1A0033] text-white pb-16 text-sm overflow-hidden relative">
        {/* 第一層 Nav */}
        <nav className="flex items-center justify-between p-4 md:px-16 lg:px-24 xl:px-32 md:py-6 w-full z-50">
          <a href="https://prebuiltui.com"></a>

          {/* 電腦模式註冊*/}
          <button className="hidden md:block bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-full transition">
            電腦模式註冊
          </button>

          {/* 手機模式會出現漢堡選單 */}
          <button
            onClick={() => setIsMenuOpen(true)}
            className="md:hidden bg-gray-900 hover:bg-gray-800 text-white p-2 rounded-md"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M4 12h16M4 18h16M4 6h16" />
            </svg>
          </button>
        </nav>
        {/* 第二層 Nav */}
        <nav className="flex items-center border mx-4 w-full max-w-4xl justify-between border-slate-700 px-4 py-2.5 rounded-full text-white">
          <a href="https://prebuiltui.com">平台名稱logo 可以放 SVG</a>
          {/* 中間路由選單 */}
          <div
            id="menu"
            class="max-md:absolute max-md:bg-black/50 max-md:backdrop-blur max-md:top-0 transition-all duration-300 max-md:h-full max-md:w-full max-md:z-10 max-md:-left-full max-md:justify-center flex-col md:flex-row flex items-center gap-2"
          >
            <a href="/" className="px-4 py-2">
              首頁
            </a>

            <div
              className="relative"
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            >
              <button className="flex items-center gap-1 hover:text-gray-300">
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
              </button>

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
          </div>
          {/*  */}
        </nav>

        {/* TODO: 預期放最新一筆玩家刊登的道具 */}
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
          全台首創娛樂性交易所
        </h1>

        <p className="text-slate-100 md:text-base text-center max-w-xl mt-3 max-md:px-4">
          熱門遊戲線上交易媒合平台
        </p>

        {/* Code Snippet */}
        <div className="bg-gradient-to-t from-indigo-900 to-slate-600 p-px rounded-md mt-8">
          <div className="flex items-center justify-between bg-black rounded-md px-4 py-3">
            <span className="font-mono text-sm">推薦馬</span>
            <button onClick={handleCopy} className="transition">
              {isCopied ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#fff"
                  strokeWidth="2"
                >
                  <path d="M20 6 9 17l-5-5" />
                </svg>
              ) : (
                <svg width="17" height="17" viewBox="0 0 17 17" fill="none">
                  <path
                    d="M14.498 5.5h-7.5a1.5 1.5 0 0 0-1.5 1.5v7.5a1.5 1.5 0 0 0 1.5 1.5h7.5a1.5 1.5 0 0 0 1.5-1.5V7a1.5 1.5 0 0 0-1.5-1.5"
                    stroke="#fff"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M2.5 11.5c-.825 0-1.5-.675-1.5-1.5V2.5C1 1.675 1.675 1 2.5 1H10c.825 0 1.5.675 1.5 1.5"
                    stroke="#fff"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>
      </section>
    </>
  );
}
