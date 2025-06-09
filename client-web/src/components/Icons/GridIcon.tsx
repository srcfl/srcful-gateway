import React from 'react';

const GridIcon: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <svg
      className={className}
      width="60"
      height="60"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M3 3V21M21 3V21M3 3H21M3 21H21M3 9H21M3 15H21M9 3V21M15 3V21"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle
        cx="6"
        cy="6"
        r="1"
        fill="currentColor"
      />
      <circle
        cx="12"
        cy="6"
        r="1"
        fill="currentColor"
      />
      <circle
        cx="18"
        cy="6"
        r="1"
        fill="currentColor"
      />
    </svg>
  );
};

export default GridIcon; 