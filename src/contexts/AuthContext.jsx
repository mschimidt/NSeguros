import React, { createContext, useContext, useState, useEffect } from 'react';
import { auth, firebaseConfig } from '../services/firebase';
import { onAuthStateChanged, signInWithEmailAndPassword, signOut } from 'firebase/auth';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);

  useEffect(() => {
    // Verifica se as chaves são as placeholders (Modo Demo)
    if (firebaseConfig.apiKey === "SUA_API_KEY") {
        console.warn("⚠️ App rodando em modo DEMO (Sem conexão Firebase Real)");
        setIsDemoMode(true);
        // Tenta recuperar sessão demo do localStorage
        const savedUser = localStorage.getItem('demo_user');
        if (savedUser) setUser(JSON.parse(savedUser));
        setLoading(false);
        return;
    }

    // Se tiver chaves reais, usa o listener do Firebase
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const login = async (email, password) => {
    if (isDemoMode) {
        // Simula um login bem sucedido (qualquer senha serve no modo demo)
        return new Promise((resolve) => {
            setTimeout(() => {
                const demoUser = { uid: 'demo-123', email: email, isDemo: true };
                setUser(demoUser);
                localStorage.setItem('demo_user', JSON.stringify(demoUser));
                resolve(demoUser);
            }, 800);
        });
    }
    // Login real
    return signInWithEmailAndPassword(auth, email, password);
  };

  const logout = async () => {
    if (isDemoMode) {
        setUser(null);
        localStorage.removeItem('demo_user');
        return Promise.resolve();
    }
    return signOut(auth);
  };

  const value = {
    user,
    login,
    logout,
    loading,
    isDemoMode
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};