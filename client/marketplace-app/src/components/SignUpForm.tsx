import React from "react";
import DiscordIcon from "./DiscordIcon";

const SignUpForm = ({ buttonClasses, buttonForGFT, toggleSignUpMode }) => {
  return (
    <div className="w-full bg-white rounded-lg shadow-xl md:mt-0 sm:max-w-md xl:p-0 border border-gray-100">
      <div className="p-6 space-y-6 md:space-y-7 sm:p-8">
        <h1 className="text-xl font-bold leading-tight tracking-tight text-backgroundColor md:text-2xl text-center">
          平台不介入玩家的現金交易
          <p className="text-sm font-normal text-gray-500 mt-1">
            現在就立即註冊 !
          </p>
        </h1>

        <form className="space-y-5 md:space-y-6" action="#">
          <div className="grid grid-cols-2 lg:grid-cols-1 gap-5 md:gap-6">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <svg
                  className="w-5 h-5 text-gray-500"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                    clipRule="evenodd"
                  ></path>
                </svg>
              </div>
              <input
                type="text"
                name="fullName"
                id="fullName"
                className="bg-[#d5f2ec] border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-brightColor focus:border-brightColor block w-full pl-10 p-3 transition-all duration-200 shadow-sm"
                placeholder="輸入帳號..(6-14字元，由字母、數字或_組成)"
                required
              />
            </div>

            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <svg
                  className="w-5 h-5 text-gray-500"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fillRule="evenodd"
                    d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                    clipRule="evenodd"
                  ></path>
                </svg>
              </div>
              <input
                type="password"
                name="password"
                id="password"
                className="bg-[#d5f2ec] border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-brightColor focus:border-brightColor block w-full pl-10 p-3 transition-all duration-200 shadow-sm"
                placeholder="輸入密碼..(6-20字元，字母區分大小寫)"
                required
              />
            </div>

            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <svg
                  className="w-5 h-5 text-gray-500"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fillRule="evenodd"
                    d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                    clipRule="evenodd"
                  ></path>
                </svg>
              </div>
              <input
                type="password"
                name="confirmPassword"
                id="confirmPassword"
                className="bg-[#d5f2ec] border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-brightColor focus:border-brightColor block w-full pl-10 p-3 transition-all duration-200 shadow-sm"
                placeholder="再次輸入密碼..(6-20字元，字母區分大小寫)"
                required
              />
            </div>
          </div>

          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                id="terms"
                aria-describedby="terms"
                type="checkbox"
                className="w-4 h-4  rounded bg-gray-50 "
                required
              />
            </div>
            <div className="ml-3 text-sm">
              <label
                htmlFor="terms"
                className="text-gray-500 hover:text-gray-700 cursor-pointer"
              >
                我已仔細閱讀並明瞭等內容，
                <a
                  href="#"
                  className="text-brightColor hover:text-brightColor font-medium"
                >
                  「服務條款」、「免責聲明」、
                </a>{" "}
                、{" "}
                <a
                  href="#"
                  className="text-brightColor hover:text-brightColor font-medium"
                >
                  「隱私權聲明」
                </a>
                同意相關規定並願遵守網站規則。
              </label>
            </div>
          </div>

          <button type="submit" className={buttonClasses}>
            立即註冊
          </button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">第三方註冊</span>
          </div>
        </div>

        <div className="">
          {/* Discord */}
          <a className="flex items-center py-2 px-4 rounded-lg bg-[#5865F2] hover:bg-[#5865F2]/80 hover:text-white/80 hover:scale-[1.02] hover:shadow-md transition-colors duration-300">
            <DiscordIcon className="h-7 w-7 fill-white hover:fill-white/80 mr-4" />
            <span className="tex-sm">Discord 註冊</span>
          </a>
        </div>

        <p
          className="text-sm text-center text-gray-600 mt-4 border-t border-gray-100 pt-4"
          onClick={toggleSignUpMode}
        >
          {`<`}返回登入
        </p>
      </div>
    </div>
  );
};

export default SignUpForm;
