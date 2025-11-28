import * as React from "react";
const SVGComponent = (props) => (
  <svg
    width="200"
    height="50"
    viewBox="0 0 400 150"
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect width="400" height="150" fill="#0066FF" rx="20" />

    <g transform="translate(40, 40)">
      <rect x="0" y="20" width="60" height="8" fill="#FFB800" rx="4" />
      <rect x="0" y="35" width="80" height="8" fill="#00D4FF" rx="4" />
      <rect x="0" y="50" width="50" height="8" fill="#FFB800" rx="4" />

      <rect
        x="90"
        y="10"
        width="8"
        height="60"
        fill="#FFFFFF"
        opacity="0.9"
        rx="4"
      />
      <rect x="103" y="0" width="8" height="70" fill="#FFB800" rx="4" />
    </g>

    <text
      x="200"
      y="70"
      font-family="Arial, sans-serif"
      font-size="48"
      font-weight="bold"
      fill="#FFFFFF"
      text-anchor="start"
    >
      秒寶
    </text>
    <text
      x="200"
      y="100"
      font-family="Arial, sans-serif"
      font-size="20"
      fill="#00D4FF"
      text-anchor="start"
    >
      交易所
    </text>
    <text
      x="200"
      y="120"
      font-family="Arial, sans-serif"
      font-size="14"
      fill="#FFFFFF"
      opacity="0.8"
      text-anchor="start"
    >
      EXCHANGE
    </text>
  </svg>
);
export default SVGComponent;
