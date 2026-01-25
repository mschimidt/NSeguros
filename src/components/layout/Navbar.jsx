import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, Menu, X, Users, AlertTriangle, LogOut, UploadCloud } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export const Navbar = () => {
  const { logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const getTitle = () => {
    if (location.pathname === '/expiring') return 'A Vencer';
    if (location.pathname === '/import') return 'Importar Dados';
    return 'Carteira';
  };

  return (
    <header className="bg-blue-600 text-white p-4 sticky top-0 z-40 shadow-md">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="p-1.5 bg-blue-500 rounded-lg">
            <Shield size={20} className="text-white" />
          </div>
          <h1 className="font-bold text-lg">{getTitle()}</h1>
        </div>

        <div className="relative">
          <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="p-2 hover:bg-blue-500 rounded focus:outline-none">
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>

          {isMenuOpen && (
            <>
              <div className="fixed inset-0 z-40 bg-black/20" onClick={() => setIsMenuOpen(false)}></div>
              <div className="absolute right-0 top-12 w-64 bg-white rounded-xl shadow-xl z-50 overflow-hidden text-gray-800 animate-in slide-in-from-top-2">
                <nav className="flex flex-col">
                  <Link to="/" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-3 p-4 hover:bg-gray-50 border-b border-gray-100">
                    <Users size={18} /> Carteira de Clientes
                  </Link>
                  <Link to="/expiring" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-3 p-4 hover:bg-gray-50 border-b border-gray-100">
                    <AlertTriangle size={18} /> Seguros a Vencer
                  </Link>
                  <Link to="/import" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-3 p-4 hover:bg-gray-50 border-b border-gray-100 bg-gray-50">
                    <UploadCloud size={18} /> Atualizar Base (XLS)
                  </Link>
                  <button onClick={logout} className="flex items-center gap-3 p-4 hover:bg-red-50 text-red-600 text-left">
                    <LogOut size={18} /> Sair do Sistema
                  </button>
                </nav>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};