"use client";
import React, { useState } from "react";
import log from "@/public/signin.svg";
import register from "@/public/signup.svg";
import SignInForm from "../components/SignInForm";
import SignUpForm from "../components/SignUpForm";

const SlidingLoginSignup = () => {
  const [isSignUpMode, setIsSignUpMode] = useState(false);

  const toggleSignUpMode = () => {
    setIsSignUpMode(!isSignUpMode);
  };

  // Common button styles
  const buttonClasses = `w-full text-white bg-backgroundColor hover:bg-brightColor focus:ring-4 focus:outline-none 
    focus:ring-primary-300 font-medium rounded-lg text-sm px-5 py-3 text-center transition-all 
    duration-200 transform hover:scale-[1.02] hover:shadow-md`;
  const buttonForGFT = `inline-flex w-full justify-center items-center rounded-lg border border-gray-300 bg-white 
    py-2.5 px-4 text-sm font-medium text-gray-500 hover:bg-gray-50 shadow-sm transition-all 
    duration-200 hover:shadow hover:border-gray-400`;

  return (
    <div>
      {/* 主要區分兩大塊，登入登出的文字訊息以及登入註冊面板區域，都先把這兩區域定位在最左上角 */}

      {/* 1. 登入登出的文字訊息 */}
      {/* TODO: 下次處理 登入面板對應的文字 跟 登出面板對應的文字的定位，因為要做滑出效果 */}
      <div className="absolute w-full h-full top-0 left-0">
        {/* 右邊是登入面板，左邊是登入面板顯示的文字訊息 */}
        <div
        // className={`flex flex-row justify-around lg:flex-col items-center  max-lg:col-start-1 max-lg:col-end-2
        //   max-lg:px-[8%] max-lg:py-10 lg:items-end  text-center z-6  max-lg:row-start-1 max-lg:row-end-2
        //    pl-[12%] pr-[17%] pt-12 pb-8 ${
        //      isSignUpMode ? "pointer-events-none" : "pointer-events-auto"
        //    }`}
        >
          <div
            className={`text-white transition-transform duration-[0.9s]  lg:duration-[1.1s] ease-[ease-in-out]
             delay-[0.8s] lg:delay-[0.4s] max-lg:pr-[15%]  max-md:px-4  max-md:py-2 ${
               isSignUpMode
                 ? "lg:translate-x-[-800px] max-lg:translate-y-[-300px]"
                 : ""
             }`}
          >
            <h3 className="font-semibold leading-none text-[1.2rem] lg:text-[1.5rem] text-gray-700">
              第一次來?
            </h3>
            <p className="text-[0.7rem] lg:text-[0.95rem] px-0 py-2 lg:py-[0.7rem] text-gray-700">
              加入我們，一起探索台服玩家熱愛的寶物交易平台！
            </p>
            <button
              className="bg-transparent w-[110px] h-[35px] text-gray-700 text-[0.7rem] lg:w-[130px] lg:h-[41px] 
              lg:text-[0.8rem]  font-semibold   border-2 border-white rounded-full transition-colors duration-300 
              hover:bg-white hover:text-gray-700"
              id="sign-up-btn"
              onClick={toggleSignUpMode}
            >
              立即註冊
            </button>
          </div>
        </div>
        {/* 左邊是註冊面板，右邊是註冊面板顯示的文字訊息 */}
        <div
        // className={`flex flex-row   max-lg:row-start-3 max-lg:row-end-4 lg:flex-col items-center lg:items-end
        //   justify-around text-center z-[6]   max-lg:col-start-1 max-lg:col-end-2  max-lg:px-[8%]   max-lg:py-10
        //    pl-[17%] pr-[12%] pt-12 pb-8 ${
        //      isSignUpMode ? " pointer-events-auto" : "pointer-events-none"
        //    }`}
        >
          <div
          // className={`text-white transition-transform duration-[0.9s] lg:duration-[1.1s] ease-in-out delay-[0.8s]
          //  lg:delay-[0.4s] max-lg:pr-[15%] max-md:px-4  max-md:py-2 ${
          //    isSignUpMode
          //      ? ""
          //      : "lg:translate-x-[800px] max-lg:translate-y-[300px]"
          //  }`}
          >
            <h3 className="font-semibold leading-none text-[1.2rem] lg:text-[1.5rem] text-gray-700">
              已經註冊了 ?
            </h3>
            <p className=" py-2 text-[0.7rem] lg:text-[0.95rem] px-0  lg:py-[0.7rem] text-gray-700">
              登入後一鍵上架虛寶，全服土豪直接搶瘋！🔥💨
            </p>
            <button
              className=" text-gray-700 bg-transparent w-[110px] h-[35px]  text-[0.7rem] lg:w-[130px] 
              lg:h-[41px] lg:text-[0.8rem]  font-semibold   border-2 border-white rounded-full 
              transition-colors duration-300 hover:bg-white hover:text-gray-700"
              id="sign-in-btn"
              onClick={toggleSignUpMode}
            >
              立即登入
            </button>
          </div>
        </div>
      </div>

      {/* 2. 登入註冊面板區域 */}
      <div className="absolute w-full h-full top-0 left-0">
        {/* 以轉場滑入方式元素進入中間位置，進入手機模式時移動的比較慢，轉場城桌面時一定的快一些。 */}
        {/* 製作方式: 先把登入登出面板想辦法置中，解決後透過mode去控制登入或登出模式，以 lg:left-1/x 方式將面板定位在特定位置，這樣mode切換後，就會有登入登出面板左右切換的效果，接著，再把面板對應的文字區域以滑出方式處理，就會有互動效果*/}
        {/* lg >= 1024px */}
        {/* max-lg < 1024px */}
        <div
          className={`centered-grid w-full duration-1000 lg:duration-700 ease-[ease-in-out]  ${
            isSignUpMode ? "lg:left-1/4" : "lg:left-3/4 "
          } `}
        >
          {/* 登入面板 isSignUpMode = false */}
          <div
            className={`flex items-center justify-center flex-col transition-all duration-[0.02s] delay-[0.2s] 
              overflow-hidden col-start-1 col-end-2 row-start-1 row-end-2 px-20 max-lg:mt-60 z-20 max-md:px-6 
              max-md:py-0 ${isSignUpMode ? "" : "opacity-100 z-20"}`}
          >
            <SignInForm
              buttonClasses={buttonClasses}
              buttonForGFT={buttonForGFT}
              toggleSignUpMode={toggleSignUpMode}
            />
          </div>
          {/* 註冊面板 isSignUpMode = true */}
          <div
            className={`flex items-center justify-center flex-col px-20 transition-all ease-in-out duration-[0.2s]
               delay-[0.7s] overflow-hidden col-start-1 col-end-2 row-start-1 row-end-2 py-0 z-10 max-md:px-6 
               max-md:py-0 opacity-0 ${
                 isSignUpMode ? "opacity-100 z-20 " : "  "
               }`}
          >
            <SignUpForm
              buttonClasses={buttonClasses}
              buttonForGFT={buttonForGFT}
              toggleSignUpMode={toggleSignUpMode}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SlidingLoginSignup;
