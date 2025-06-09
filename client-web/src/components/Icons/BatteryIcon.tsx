import React from 'react';

const BatteryIcon: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <svg
      className={className}
      width="60"
      height="60"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect
        x="3"
        y="6"
        width="16"
        height="12"
        rx="2"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
      />
      <rect
        x="21"
        y="9"
        width="1"
        height="6"
        rx="0.5"
        fill="currentColor"
      />
      <rect
        x="5"
        y="8"
        width="12"
        height="8"
        rx="1"
        fill="currentColor"
        opacity="0.3"
      />
    </svg>
  );
};

export default BatteryIcon; 