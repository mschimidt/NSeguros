import re
import os

def update_firebase_config():
    print("--- Configuração do Frontend React ---")
    print("Acesse: Firebase Console > Project Settings (Engrenagem) > General > Your apps > SDK Setup and Configuration")
    print("Copie os valores correspondentes abaixo:\n")

    api_key = input("apiKey: ").strip()
    auth_domain = input("authDomain: ").strip()
    project_id = input("projectId: ").strip()
    storage_bucket = input("storageBucket: ").strip()
    messaging_sender_id = input("messagingSenderId: ").strip()
    app_id = input("appId: ").strip()

    js_content = f"""import {{ initializeApp }} from "firebase/app";
import {{ getAuth }} from "firebase/auth";
import {{ getFirestore }} from "firebase/firestore";

// --- CONFIGURAÇÃO REAL ---
export const firebaseConfig = {{
  apiKey: "{api_key}",
  authDomain: "{auth_domain}",
  projectId: "{project_id}",
  storageBucket: "{storage_bucket}",
  messagingSenderId: "{messaging_sender_id}",
  appId: "{app_id}"
}};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export default app;
"""

    file_path = "src/services/firebase.js"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"\n✅ Arquivo '{file_path}' atualizado com sucesso!")
    print("🔄 O Vite deve recarregar a página automaticamente.")
    print("⚠️ IMPORTANTE: Agora você precisa fazer LOGIN com um usuário real cadastrado no 'Authentication' do Firebase.")

if __name__ == "__main__":
    update_firebase_config()