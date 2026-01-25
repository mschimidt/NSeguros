# Guia de Publicação - CRM Seguros

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
