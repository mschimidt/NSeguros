import subprocess
import pandas as pd
import os
import shutil
import time
import sys

# --- CONFIGURAÇÕES ---
INPUT_MDB = "DADOS.MDB"  # Nome do arquivo que você vai jogar na pasta
OUTPUT_XLS = "DADOS.xls" # Nome do arquivo que o sistema lê

# Tabelas que precisamos extrair para o sistema funcionar
TARGET_TABLES = [
    'clientes', 'seguros', 'produtores', 'ramos', 
    'marcas', 'seguradoras', 'coberturas', 'licencia'
]

def install_deps():
    """Garante que as libs python estejam instaladas"""
    try:
        import xlsxwriter
    except ImportError:
        print("📦 Instalando biblioteca xlsxwriter...")
        os.system("pip install xlsxwriter")

def check_system_deps():
    """Verifica se o mdbtools (Linux) está instalado"""
    if shutil.which('mdb-export') is None:
        print("❌ ERRO CRÍTICO: 'mdb-tools' não encontrado.")
        print("👉 Para corrigir, rode no terminal:")
        print("   sudo apt-get update && sudo apt-get install mdbtools -y")
        return False
    return True

def convert_mdb_to_excel():
    if not check_system_deps(): return False
    
    if not os.path.exists(INPUT_MDB):
        print(f"⚠️  Arquivo '{INPUT_MDB}' não encontrado na raiz.")
        print("   Faça o upload do seu arquivo .MDB para a pasta do projeto.")
        return False

    print(f"🚀 Iniciando conversão: {INPUT_MDB} -> {OUTPUT_XLS}...")
    
    try:
        # Usamos xlsxwriter para gerar um Excel (.xlsx) que renomeamos para .xls 
        # (para manter compatibilidade com o nome que o script de importação espera)
        writer = pd.ExcelWriter(OUTPUT_XLS, engine='xlsxwriter')
        found_tables = 0

        # 1. Lista todas as tabelas do arquivo MDB
        # Executa comando linux 'mdb-tables'
        tables_cmd = subprocess.run(['mdb-tables', '-1', INPUT_MDB], capture_output=True, text=True)
        all_tables = tables_cmd.stdout.splitlines()

        # 2. Itera sobre as tabelas desejadas
        for table in TARGET_TABLES:
            if table in all_tables:
                print(f"   🔹 Processando tabela: {table}...")
                
                # Extrai para CSV na memória usando 'mdb-export'
                cmd = ['mdb-export', INPUT_MDB, table]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                
                if proc.returncode == 0:
                    from io import StringIO
                    # Lê o CSV da memória com Pandas
                    df = pd.read_csv(StringIO(proc.stdout))
                    
                    # Salva como uma aba no arquivo Excel
                    df.to_excel(writer, sheet_name=table, index=False)
                    found_tables += 1
                else:
                    print(f"   ⚠️ Falha ao exportar tabela {table}")
            else:
                print(f"   ⚠️ Tabela '{table}' não encontrada no MDB.")

        writer.close()
        print(f"\n✅ SUCESSO! {found_tables} tabelas convertidas.")
        print(f"📁 Arquivo gerado: {OUTPUT_XLS}")
        return True

    except Exception as e:
        print(f"❌ Erro fatal na conversão: {e}")
        return False

# --- MODO AUTOMÁTICO (WATCHER) ---
def watch_folder():
    print(f"\n👀 MODO VIGIA ATIVO")
    print(f"   Aguardando arquivo '{INPUT_MDB}' ser modificado ou criado...")
    print("   (Pressione Ctrl+C para parar)")
    
    last_mtime = 0
    
    while True:
        try:
            if os.path.exists(INPUT_MDB):
                current_mtime = os.path.getmtime(INPUT_MDB)
                # Se o arquivo foi modificado recentemente
                if current_mtime > last_mtime:
                    print("\n🔄 Detactada alteração no arquivo MDB!")
                    # Espera 1 segundo para garantir que o upload terminou
                    time.sleep(1)
                    if convert_mdb_to_excel():
                        print("👉 Agora você pode ir no App e clicar em 'Importar > Iniciar Atualização'")
                    last_mtime = current_mtime
            
            time.sleep(3) # Verifica a cada 3 segundos
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro no watcher: {e}")

if __name__ == "__main__":
    install_deps()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--watch':
        watch_folder()
    else:
        convert_mdb_to_excel()