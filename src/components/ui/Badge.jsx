import React from 'react';

export const Badge = ({ status }) => {
  const colors = status === 'Ativo' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  return <span className={`px-2 py-1 rounded-full text-xs font-bold ${colors}`}>{status}</span>;
};