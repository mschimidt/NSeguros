import React from 'react';

export const Card = ({ children, className = "", onClick }) => (
  <div 
    onClick={onClick} 
    className={`bg-white rounded-xl shadow-sm border border-gray-100 p-4 ${className} ${onClick ? 'active:scale-95 transition-transform cursor-pointer' : ''}`}
  >
    {children}
  </div>
);