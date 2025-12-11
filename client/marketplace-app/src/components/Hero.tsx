import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Hero() {
  const [input, setInput] = useState("");

  const navigate = useNavigate();

  const onSubmitHandler = (e: { preventDefault: () => void }) => {
    e.preventDefault();
    navigate(`/marketplace?search=${input}`);
  };

  // https://prebuiltui.com/components/hero-section#hero-section-with-banner-84fb
  //  參考上面版型

  return (
    <>
      <div className="flex flex-col items-center  text-black pb-16 text-sm overflow-hidden relative">
        <p className="md:text-base text-center max-w-xl mt-3 mb-3 max-md:px-4">
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
      </div>
    </>
  );
}
