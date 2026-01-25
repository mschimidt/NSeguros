import os

# Definição da estrutura de diretórios e arquivos baseada no README
structure = {
    "public": [
        "manifest.json",
        "sw.js",
        # Nota: apple-touch-icon.png deve ser uma imagem, não criando arquivo de texto vazio
    ],
    "src": {
        "assets": [],
        "components": {
            "ui": [],     # Botões, Cards, Inputs
            "layout": []  # Navbar, Sidebar
        },
        "contexts": [
            "AuthContext.jsx"
        ],
        "hooks": [],      # useClients.js, usePolicies.js
        "pages": [
            "Login.jsx",
            "ClientList.jsx",
            "ClientDetail.jsx"
        ],
        "services": [
            "firebase.js",
            "auth.js"
        ],
        "utils": [],
        "": [             # Arquivos na raiz de src/
            "App.jsx",
            "main.jsx"
        ]
    },
    "": [                 # Arquivos na raiz do projeto
        "migrate_data.py",
        "vite.config.js",
        # package.json geralmente é criado pelo npm init, mas criaremos o placeholder
        "package.json" 
    ]
}

def create_structure(base_path, struct):
    for name, content in struct.items():
        path = os.path.join(base_path, name) if name else base_path
        
        if isinstance(content, dict):
            # É um diretório com subdiretórios
            if name: # Evita tentar criar diretório vazio se for a raiz
                os.makedirs(path, exist_ok=True)
                print(f"📁 Criado diretório: {path}")
            create_structure(path, content)
            
        elif isinstance(content, list):
            # É uma lista de arquivos dentro do diretório atual
            if name:
                os.makedirs(path, exist_ok=True)
                print(f"📁 Criado diretório: {path}")
            
            for filename in content:
                file_path = os.path.join(path, filename)
                if not os.path.exists(file_path):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        # Adiciona um comentário básico dependendo da extensão
                        if filename.endswith('.jsx') or filename.endswith('.js'):
                            f.write(f"// Arquivo: {filename}\n")
                        elif filename.endswith('.json'):
                            f.write("{}")
                        elif filename.endswith('.py'):
                            f.write(f"# Script: {filename}\n")
                    print(f"  📄 Criado arquivo: {file_path}")
                else:
                    print(f"  ⚠️  Arquivo já existe: {file_path}")

if __name__ == "__main__":
    print("--- Iniciando Configuração do Projeto CRM Seguros ---")
    current_dir = os.getcwd()
    create_structure(current_dir, structure)
    print("\n✅ Estrutura de diretórios criada com sucesso!")
    print("👉 Agora você pode copiar o código do 'App.jsx' gerado anteriormente e distribuir nos arquivos correspondentes.")