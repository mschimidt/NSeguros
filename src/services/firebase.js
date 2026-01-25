import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// --- CONFIGURAÇÃO REAL ---
export const firebaseConfig = {
  apiKey: "AIzaSyBHGorZeXgigt0XkTQ-W8YqRUOKCpykP8g",
  authDomain: "nseguros-931bd.firebaseapp.com",
  projectId: "nseguros-931bd",
  storageBucket: "nseguros-931bd.firebasestorage.app",
  messagingSenderId: "673587632109",
  appId: "1:673587632109:web:c340154aa07e59fe1bf9e4"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export default app;
