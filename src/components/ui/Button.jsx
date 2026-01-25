import React from 'react';

export const Button = ({ children, onClick, variant = 'primary', className = "", type="button", disabled=false }) => {
  const baseStyle = "w-full py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors focus:ring-2 focus:ring-offset-1 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 focus:ring-blue-500",
    outline: "border-2 border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500",
    danger: "bg-red-50 text-red-600 hover:bg-red-100 focus:ring-red-500"
  };
  return (
    <button 
      type={type} 
      onClick={onClick} 
      disabled={disabled}
      className={`${baseStyle} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
};