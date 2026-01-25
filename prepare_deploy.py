import os

# Conteúdo dos arquivos de deploy
files_content = {
    # 1. DOCKERFILE (Para o servidor Python no Render)
    # Instala Python, mdbtools e suas dependências num ambiente Linux limpo
    "Dockerfile": """FROM python:3.9-slim

# Instala mdbtools (Driver do Access) e gunicorn (Servidor Web)
RUN apt-get update && apt-get install -y \\
    mdbtools \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copia o código do servidor
COPY api_server.py .

# Expõe a porta e roda o servidor com Gunicorn (Produção)
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "api_server:app"]
""",

    # 2. Atualização do package.json com scripts de deploy
    "package.json": """{
  "name": "crm-seguros",
  "private": true,
  "version": "1.2.0",
  "type": "module",
  "homepage": "https://SEU_USUARIO.github.io/NOME_DO_REPO",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "predeploy": "npm run build",
    "deploy": "gh-pages -d dist"
  },
  "dependencies": {
    "firebase": "^10.7.1",
    "lucide-react": "^0.300.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.1",
    "xlsx": "^0.18.5"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.3",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.27",
    "tailwindcss": "^3.3.3",
    "vite": "^4.4.5",
    "vite-plugin-pwa": "^0.16.4",
    "gh-pages": "^6.1.1"
  }
}""",

    # 3. Manual de Instruções
    "DEPLOY.md": """# Guia de Publicação - CRM Seguros

Siga estes passos para colocar seu sistema no ar.

## Parte 1: Publicar o Backend (Servidor de Conversão)
O backend Python precisa rodar em um servidor que suporte Docker. Usaremos o **Render** (plano gratuito).

1. Faça **Commit** e **Push** de todo o seu código para o seu repositório no GitHub.
   - No VS Code: Aba Source Control > Mensagem "Deploy" > Commit > Sync Changes.
2. Crie uma conta no [Render.com](https://render.com).
3. Clique em **New +** e selecione **Web Service**.
4. Conecte sua conta do GitHub e selecione o repositório `NSeguros`.
5. Configure:
   - **Name:** `crm-backend` (ou o que preferir)
   - **Runtime:** Selecione **Docker** (Isso é importante!)
   - **Region:** Ohio ou Frankfurt (Free tier)
   - **Instance Type:** Free
6. Clique em **Create Web Service**.
7. Aguarde o deploy (pode levar uns 5 min). Quando terminar, copie a URL gerada (ex: `https://crm-backend.onrender.com`).

---

## Parte 2: Configurar o Frontend
Agora precisamos dizer ao React onde está o backend que acabamos de criar.

1. Volte ao Codespaces.
2. Abra o arquivo `src/pages/DataImport.jsx`.
3. Localize a linha `const API_URL = ...` (perto do topo).
4. Substitua `'https://SEU-APP-NO-RENDER.onrender.com'` pela URL real que você copiou do Render.
5. Abra o arquivo `package.json` e edite a linha `"homepage"`:
   - De: `"https://SEU_USUARIO.github.io/NOME_DO_REPO"`
   - Para: A URL do seu GitHub Pages (ex: `https://mschimidt.github.io/NSeguros`).

---

## Parte 3: Publicar o Frontend (App)
Vamos hospedar o visual no GitHub Pages.

1. No terminal do Codespaces, instale a ferramenta de deploy:
   `npm install`
2. Execute o comando de publicação:
   `npm run deploy`
3. O sistema vai criar uma branch `gh-pages` no seu repositório.
4. Acesse seu repositório no GitHub > Settings > Pages.
5. Verifique se "Source" está como `Deploy from a branch` e a branch é `gh-pages`.
6. Seu site estará no ar em alguns minutos! 🚀
"""
}

def create_deploy_files():
    print("--- Gerando Arquivos de Deploy ---")
    current_dir = os.getcwd()
    
    for filename, content in files_content.items():
        file_path = os.path.join(current_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Criado/Atualizado: {filename}")

if __name__ == "__main__":
    create_deploy_files()
    print("\\n🎉 Arquivos gerados!")
    print("👉 Abra o arquivo 'DEPLOY.md' para ver o passo a passo da publicação.")