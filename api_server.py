from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import subprocess
import os
import shutil
from io import StringIO
import traceback
import sys

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

TARGET_TABLES = [
    'clientes', 'seguros', 'produtores', 'ramos', 
    'marcas', 'seguradoras', 'coberturas', 'licencia'
]

def check_and_install_mdbtools():
    if shutil.which('mdb-export') is not None:
        return True
    print("⚠️ [API] 'mdbtools' não encontrado. Tentando instalar automaticamente...")
    try:
        subprocess.run(['sudo', 'apt-get', 'update', '--allow-releaseinfo-change'], check=False) 
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'mdbtools'], check=True)
        print("✅ [API] 'mdbtools' instalado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ [API] Falha na instalação automática: {e}")
        return False

@app.route('/', methods=['GET'])
def home():
    return "CRM Seguros API Online"

@app.route('/api/convert-mdb', methods=['POST'])
def convert_mdb():
    print(">>> [API] Recebendo requisição POST /api/convert-mdb")
    if shutil.which('mdb-export') is None:
        return jsonify({"error": "Dependência 'mdbtools' não encontrada no servidor."}), 500
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    file = request.files['file']
    filename = "temp_upload.mdb"
    try:
        file.save(filename)
        print(f"✅ [API] Arquivo salvo: {filename}")
    except Exception as e:
        return jsonify({"error": f"Falha ao salvar arquivo: {str(e)}"}), 500
    result_data = {}
    try:
        print(">>> [API] Extraindo tabelas...")
        tables_cmd = subprocess.run(['mdb-tables', '-1', filename], capture_output=True, text=True)
        if tables_cmd.returncode != 0:
            raise Exception(f"Arquivo inválido: {tables_cmd.stderr}")
        all_tables = tables_cmd.stdout.splitlines()
        for table in TARGET_TABLES:
            if table in all_tables:
                cmd = ['mdb-export', filename, table]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                if proc.returncode == 0:
                    try:
                        df = pd.read_csv(StringIO(proc.stdout))
                        df = df.fillna('')
                        result_data[table] = df.to_dict(orient='records')
                    except Exception as pd_err:
                        print(f"⚠️ Erro ao ler tabela {table}: {pd_err}")
        if os.path.exists(filename): os.remove(filename)
        print("✅ [API] Conversão concluída.")
        return jsonify({"success": True, "data": result_data})
    except Exception as e:
        if os.path.exists(filename): os.remove(filename)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    ready = shutil.which('mdb-export') is not None
    return jsonify({"status": "online", "mdbtools": ready})

if __name__ == '__main__':
    check_and_install_mdbtools()
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Servidor Python iniciado na porta {port}")
    app.run(host='0.0.0.0', port=port)
