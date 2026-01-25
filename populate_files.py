import os

files_content = {
    # Dependências (Mantidas)
    "requirements.txt": """pandas
firebase-admin
openpyxl
xlrd
flask
flask-cors
""",

    # Vite Config (Mantido)
    "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig(({ command, mode }) => {
  return {
    plugins: [
      react(),
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
        manifest: {
          name: 'CRM Seguros',
          short_name: 'CRM',
          description: 'Gestão de Carteira de Seguros',
          theme_color: '#2563eb',
          background_color: '#f3f4f6',
          display: 'standalone',
          scope: '/',
          start_url: '/',
          orientation: 'portrait',
          icons: [
            {
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            },
            {
              src: 'pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png'
            }
          ]
        }
      })
    ],
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:5000',
          changeOrigin: true,
          secure: false
        }
      }
    }
  }
})""",

    # Backend Config (Mantido)
    "Procfile": "web: python api_server.py",

    # API Server (Mantido)
    "api_server.py": """from flask import Flask, request, jsonify
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
""",

    # Data Import (Mantido)
    "src/pages/DataImport.jsx": """import React, { useState, useEffect } from 'react';
import { read, utils } from 'xlsx';
import { db } from '../services/firebase';
import { writeBatch, doc } from 'firebase/firestore';
import { Navbar } from '../components/layout/Navbar';
import { UploadCloud, CheckCircle, Database, Loader2, AlertTriangle } from 'lucide-react';

const API_URL = import.meta.env.PROD 
    ? 'https://SEU-APP-NO-RENDER.onrender.com'
    : '';

export const DataImport = () => {
  const [loading, setLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState('checking');
  const [logs, setLogs] = useState([]);
  const [file, setFile] = useState(null);

  const addLog = (msg) => setLogs(prev => [...prev, msg]);

  useEffect(() => {
    const checkUrl = `${API_URL}/api/status`;
    fetch(checkUrl)
        .then(res => res.json())
        .then(data => setServerStatus(data.status === 'online' ? 'online' : 'offline'))
        .catch(() => setServerStatus('offline'));
  }, []);

  const cleanStr = (val) => val ? String(val).trim() : "";
  const cleanNum = (val) => val ? parseFloat(val) : 0;
  
  const parseDate = (val) => {
      if(!val) return null;
      if (typeof val === 'string' && val.includes('/')) {
         const [m, d, y] = val.split(' ')[0].split('/'); 
         if(m && d && y) return new Date(`20${y}-${m}-${d}`);
      }
      return new Date(val); 
  };

  const processMDB = async () => {
      if (!file) return;
      setLoading(true);
      setLogs([]);
      addLog("🚀 Enviando MDB para conversão...");

      try {
          const formData = new FormData();
          formData.append('file', file);

          const endpoint = `${API_URL}/api/convert-mdb`;
          const res = await fetch(endpoint, {
              method: 'POST',
              body: formData
          });
          
          const jsonResponse = await res.json().catch(() => null);

          if (!res.ok) {
              const erroMsg = jsonResponse?.error || `Erro HTTP ${res.status}`;
              throw new Error(erroMsg);
          }
          
          if (!jsonResponse || !jsonResponse.data) throw new Error("Resposta inválida do servidor");

          const data = jsonResponse.data;
          addLog("✅ Conversão concluída! Iniciando gravação...");

          const maps = { ramos: {}, seguradoras: {}, marcas: {}, produtores: {} };
          const loadMap = (tableName, mapObj, keyField, valField) => {
              if (data[tableName]) {
                  data[tableName].forEach(r => mapObj[r[keyField]] = r[valField]);
              }
          };
          loadMap('ramos', maps.ramos, 'codigo', 'ramo');
          loadMap('seguradoras', maps.seguradoras, 'codigo', 'nome');
          loadMap('marcas', maps.marcas, 'codigo', 'nome');
          loadMap('produtores', maps.produtores, 'codigo', 'nome');

          const clientMap = {}; 
          if (data['clientes']) {
              let batch = writeBatch(db);
              let count = 0;
              let total = 0;
              addLog(">>> Processando Clientes...");

              for (const row of data['clientes']) {
                  const docId = String(row['codigo']);
                  const nome = cleanStr(row['nome']).toUpperCase();
                  clientMap[row['codigo']] = nome;

                  const clientData = {
                      legacy_id: row['codigo'],
                      nome: nome,
                      search_keywords: nome.toLowerCase().split(' '),
                      cpf_cnpj: cleanStr(row['cpf'] || row['cnpj']),
                      telefones: cleanStr(row['fones']),
                      email: cleanStr(row['email']).toLowerCase(),
                      cidade: cleanStr(row['cidade']),
                      endereco: cleanStr(row['endereco']),
                      rg: cleanStr(row['numdoc']),
                      profissao: cleanStr(row['profissao']),
                      nascimento: parseDate(row['nascimento'])
                  };
                  Object.keys(clientData).forEach(k => !clientData[k] && delete clientData[k]);
                  batch.set(doc(db, "dim_clientes", docId), clientData);
                  count++;
                  if (count >= 400) { await batch.commit(); batch = writeBatch(db); total += count; count = 0; }
              }
              if (count > 0) await batch.commit();
              addLog(`✅ Clientes salvos.`);
          }

          if (data['seguros']) {
              let batch = writeBatch(db);
              let count = 0;
              addLog(">>> Processando Seguros...");

              for (const row of data['seguros']) {
                  const docId = String(row['codigo']);
                  const factData = {
                      legacy_id: row['codigo'],
                      status: String(row['ativo']) === '1' ? 'Ativo' : 'Inativo',
                      fk_cliente: String(row['cliente']),
                      dim_cliente_nome: clientMap[row['cliente']] || "DESCONHECIDO",
                      dim_seguradora_nome: maps.seguradoras[row['seguradora']] || "OUTRA",
                      dim_ramo_nome: maps.ramos[row['ramo']] || "GERAL",
                      apolice: cleanStr(row['apolice']),
                      vigencia_inicio: parseDate(row['inicio']),
                      vigencia_final: parseDate(row['final']),
                      veiculo_modelo: cleanStr(row['modelo']),
                      veiculo_placa: cleanStr(row['placa']).toUpperCase(),
                      valor_premio: cleanNum(row['valornf'])
                  };
                  Object.keys(factData).forEach(k => !factData[k] && delete factData[k]);
                  batch.set(doc(db, "fact_seguros", docId), factData);
                  count++;
                  if (count >= 400) { await batch.commit(); batch = writeBatch(db); count = 0; }
              }
              if (count > 0) await batch.commit();
              addLog(`✅ Seguros salvos.`);
          }

          addLog("🎉 Processo Finalizado!");
          alert("Base atualizada com sucesso!");

      } catch (e) {
          console.error(e);
          addLog("❌ ERRO: " + e.message);
          alert("Erro: " + e.message);
      } finally {
          setLoading(false);
      }
  };

  return (
    <div className="min-h-screen bg-slate-50 pb-20 font-sans text-gray-900">
      <Navbar />
      <main className="p-6 max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 mb-4">
                    <Database size={32} />
                </div>
                <h2 className="text-xl font-bold text-gray-800">Importação MDB</h2>
                <p className="text-gray-500 text-sm mt-2">
                    {API_URL 
                        ? "Modo Nuvem (Backend Remoto)" 
                        : "Modo Local (Codespaces)"}
                </p>
            </div>

            <div className={`mb-6 p-3 rounded-lg text-sm flex items-center gap-2 justify-center ${serverStatus === 'online' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                {serverStatus === 'online' ? <><CheckCircle size={16}/> API Online</> : <><AlertTriangle size={16}/> API Offline</>}
            </div>

            <div className="space-y-4">
                <label className="block w-full cursor-pointer">
                    <input type="file" accept=".mdb" onChange={(e) => setFile(e.target.files[0])} className="hidden" />
                    <div className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-colors ${file ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:bg-gray-50'}`}>
                        <Database size={40} className={file ? 'text-blue-500' : 'text-gray-400'} />
                        <span className="mt-2 font-medium text-gray-700">{file ? file.name : "Selecionar MDB"}</span>
                    </div>
                </label>
                <button onClick={processMDB} disabled={!file || loading || serverStatus !== 'online'} className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 disabled:opacity-50">
                    {loading ? <Loader2 className="animate-spin" /> : <UploadCloud size={20} />}
                    {loading ? "Processando..." : "Enviar"}
                </button>
            </div>

            <div className="mt-8 bg-gray-900 rounded-lg p-4 font-mono text-xs text-green-400 h-48 overflow-y-auto shadow-inner">
                {logs.map((log, i) => <div key={i} className="mb-1">{log}</div>)}
            </div>
        </div>
      </main>
    </div>
  );
};"""
,

    # ClientDetail COM CORREÇÃO DE DATA
    "src/pages/ClientDetail.jsx": """import React, { useState, useEffect } from 'react';
import { ChevronRight, Users, Phone, MapPin, FileText, Car, Edit2, Save, X, Trash2, Calendar, CreditCard, User, Mail, Briefcase } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { db } from '../services/firebase';
import { collection, query, where, getDocs, doc, updateDoc, deleteDoc } from 'firebase/firestore';
import { useAuth } from '../contexts/AuthContext';

export const ClientDetail = ({ client, onClose, onUpdate }) => {
  const { isDemoMode } = useAuth();
  const [activeTab, setActiveTab] = useState('dados'); 
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({ ...client });
  const [saving, setSaving] = useState(false);

  // --- Função para corrigir o bug do ano 20XX ---
  const formatBirthDate = (timestamp) => {
      if (!timestamp) return '';
      // Firestore Timestamp
      if (timestamp.seconds) {
          const date = new Date(timestamp.seconds * 1000);
          // Se o ano for maior que o ano atual, subtrai 100
          const currentYear = new Date().getFullYear();
          if (date.getFullYear() > currentYear) {
              date.setFullYear(date.getFullYear() - 100);
          }
          return date.toLocaleDateString('pt-BR');
      }
      return '';
  };

  useEffect(() => {
    const fetchPolicies = async () => {
      if (isDemoMode) { setLoading(false); return; }
      try {
        const searchId = client.legacy_id ? String(client.legacy_id) : client.id;
        const q = query(collection(db, "fact_seguros"), where("fk_cliente", "==", searchId));
        const snap = await getDocs(q);
        const list = snap.docs.map(d => ({ id: d.id, ...d.data() }));
        setPolicies(list);
      } catch (e) { console.error(e); } 
      finally { setLoading(false); }
    };
    fetchPolicies();
  }, [client]);

  const handleSave = async () => {
    if (isDemoMode) return;
    setSaving(true);
    try {
        const ref = doc(db, "dim_clientes", client.id);
        await updateDoc(ref, formData);
        setIsEditing(false);
        if (onUpdate) onUpdate();
    } catch (e) { alert(e.message); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
      if (!window.confirm("Excluir cliente?")) return;
      if (isDemoMode) return;
      try {
          await deleteDoc(doc(db, "dim_clientes", client.id));
          onClose();
          if (onUpdate) onUpdate();
      } catch (e) { alert(e.message); }
  };

  const InputField = ({ label, value, field, icon: Icon }) => (
    <div className="mb-3">
        <label className="text-xs text-gray-500 font-semibold mb-1 block">{label}</label>
        {isEditing ? (
            <input 
                className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:border-blue-500 outline-none"
                value={value || ''}
                onChange={e => setFormData({...formData, [field]: e.target.value})}
            />
        ) : (
            <div className="flex items-center gap-2 text-gray-800">
                {Icon && <Icon size={16} className="text-blue-500" />}
                <span className="font-medium text-sm break-all">{value || '-'}</span>
            </div>
        )}
    </div>
  );

  return (
    <div className="fixed inset-0 z-50 bg-white flex flex-col animate-in slide-in-from-right duration-300">
      <div className="bg-white border-b p-4 flex items-center gap-3 sticky top-0 z-10 shadow-sm">
        <button onClick={onClose} className="p-2 -ml-2 rounded-full hover:bg-gray-100">
          <ChevronRight className="rotate-180 text-gray-600" />
        </button>
        <div className="flex-1 truncate">
           <h2 className="text-lg font-bold text-gray-900">{isEditing ? "Editando" : "Detalhes"}</h2>
           <p className="text-xs text-gray-500">Cod: {client.legacy_id}</p>
        </div>
        {isEditing ? (
            <div className="flex gap-2">
                <button onClick={() => setIsEditing(false)} className="p-2 bg-gray-100 rounded-full"><X size={20} /></button>
                <button onClick={handleSave} disabled={saving} className="p-2 text-white bg-green-600 rounded-full"><Save size={20} /></button>
            </div>
        ) : (
            <div className="flex gap-2">
                <button onClick={handleDelete} className="p-2 text-red-500 bg-red-50 rounded-full"><Trash2 size={20} /></button>
                <button onClick={() => setIsEditing(true)} className="p-2 text-blue-600 bg-blue-50 rounded-full"><Edit2 size={20} /></button>
            </div>
        )}
      </div>

      <div className="flex border-b bg-gray-50">
          {['dados', 'enderecos', 'seguros'].map(tab => (
              <button 
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-3 text-sm font-semibold capitalize ${activeTab === tab ? 'text-blue-600 border-b-2 border-blue-600 bg-white' : 'text-gray-500'}`}
              >
                  {tab === 'enderecos' ? 'Endereços' : tab}
              </button>
          ))}
      </div>

      <div className="flex-1 overflow-y-auto p-4 bg-gray-50 pb-20">
        
        {activeTab === 'dados' && (
            <div className="space-y-4">
                <Card>
                    <h3 className="text-sm font-bold text-gray-700 mb-4 border-b pb-2">Informações Pessoais</h3>
                    <InputField label="Nome Completo" value={isEditing ? formData.nome : client.nome} field="nome" icon={User} />
                    <div className="grid grid-cols-2 gap-3">
                        <InputField label="CPF/CNPJ" value={isEditing ? formData.cpf_cnpj : client.cpf_cnpj} field="cpf_cnpj" icon={CreditCard} />
                        <InputField label="RG" value={isEditing ? formData.rg : client.rg} field="rg" />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        {/* AQUI APLICAMOS A CORREÇÃO DE DATA */}
                        <InputField label="Data Nasc." value={isEditing ? formData.nascimento : formatBirthDate(client.nascimento)} field="nascimento" icon={Calendar} />
                        <InputField label="Sexo" value={isEditing ? formData.sexo : client.sexo} field="sexo" />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <InputField label="Est. Civil" value={isEditing ? formData.estado_civil : client.estado_civil} field="estado_civil" />
                        <InputField label="Profissão" value={isEditing ? formData.profissao : client.profissao} field="profissao" icon={Briefcase} />
                    </div>
                </Card>

                <Card>
                    <h3 className="text-sm font-bold text-gray-700 mb-4 border-b pb-2">Contato</h3>
                    <InputField label="Email" value={isEditing ? formData.email : client.email} field="email" icon={Mail} />
                    <InputField label="Telefones" value={isEditing ? formData.telefones : client.telefones} field="telefones" icon={Phone} />
                </Card>

                <Card>
                    <h3 className="text-sm font-bold text-gray-700 mb-4 border-b pb-2">Documentação</h3>
                    <div className="grid grid-cols-2 gap-3">
                        <InputField label="CNH" value={isEditing ? formData.cnh : client.cnh} field="cnh" />
                        <InputField label="Validade CNH" value={isEditing ? formData.cnh_validade : (client.cnh_validade ? new Date(client.cnh_validade.seconds * 1000).toLocaleDateString('pt-BR') : '')} field="cnh_validade" />
                    </div>
                    <InputField label="Orgão Emissor" value={isEditing ? formData.orgao_emissor : client.orgao_emissor} field="orgao_emissor" />
                </Card>
            </div>
        )}

        {activeTab === 'enderecos' && (
            <div className="space-y-4">
                <Card>
                    <h3 className="text-sm font-bold text-gray-700 mb-4 border-b pb-2">Residencial</h3>
                    <InputField label="Endereço" value={isEditing ? formData.endereco : client.endereco} field="endereco" icon={MapPin} />
                    <div className="grid grid-cols-2 gap-3">
                        <InputField label="Bairro" value={isEditing ? formData.bairro : client.bairro} field="bairro" />
                        <InputField label="CEP" value={isEditing ? formData.cep : client.cep} field="cep" />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <InputField label="Cidade" value={isEditing ? formData.cidade : client.cidade} field="cidade" />
                        <InputField label="UF" value={isEditing ? formData.uf : client.uf} field="uf" />
                    </div>
                </Card>

                {(client.end_comercial || isEditing) && (
                    <Card>
                        <h3 className="text-sm font-bold text-gray-700 mb-4 border-b pb-2">Comercial / Outro</h3>
                        <InputField label="Endereço" value={isEditing ? formData.end_comercial : client.end_comercial} field="end_comercial" icon={MapPin} />
                        <div className="grid grid-cols-2 gap-3">
                            <InputField label="Bairro" value={isEditing ? formData.bairro_comercial : client.bairro_comercial} field="bairro_comercial" />
                            <InputField label="CEP" value={isEditing ? formData.cep_comercial : client.cep_comercial} field="cep_comercial" />
                        </div>
                         <div className="grid grid-cols-2 gap-3">
                            <InputField label="Cidade" value={isEditing ? formData.cidade_comercial : client.cidade_comercial} field="cidade_comercial" />
                            <InputField label="UF" value={isEditing ? formData.uf_comercial : client.uf_comercial} field="uf_comercial" />
                        </div>
                    </Card>
                )}
            </div>
        )}

        {activeTab === 'seguros' && (
            <div className="space-y-3">
                <h3 className="text-xs font-bold text-gray-500 uppercase ml-1 mb-2">Apólices Ativas e Inativas ({policies.length})</h3>
                {loading ? <p className="text-center">Carregando...</p> : (
                    policies.length === 0 ? <div className="text-center py-8 text-gray-400 border border-dashed rounded-xl">Sem seguros</div> : (
                    policies.map(p => (
                        <Card key={p.id} className={`border-l-4 ${p.status === 'Ativo' ? 'border-l-green-500' : 'border-l-gray-300'} relative`}>
                        <div className="flex justify-between items-start mb-2">
                            <span className="text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded">{p.dim_ramo_nome || 'Geral'}</span>
                            <Badge status={p.status} />
                        </div>
                        <h4 className="font-bold text-gray-800 mb-1">{p.dim_seguradora_nome}</h4>
                        <div className="text-xs text-gray-500 mb-2">Apólice: {p.apolice}</div>
                        
                        {p.veiculo && (
                            <div className="bg-gray-50 p-2 rounded mb-2 text-sm">
                                <div className="font-bold text-gray-700">{p.veiculo.modelo}</div>
                                <div className="flex gap-2 text-xs text-gray-500 mt-1">
                                    <span>{p.veiculo.placa}</span>
                                    <span>{p.veiculo.cor}</span>
                                    <span>{p.veiculo.ano_fab}/{p.veiculo.ano_mod}</span>
                                </div>
                                <div className="text-xs text-gray-400 mt-1">Chassi: {p.veiculo.chassi}</div>
                            </div>
                        )}

                        <div className="grid grid-cols-2 gap-2 text-xs border-t pt-2 mt-2">
                            <div>
                                <span className="text-gray-400 block">Vigência Início</span>
                                <span className="font-medium">{p.vigencia_inicio ? new Date(p.vigencia_inicio.seconds*1000).toLocaleDateString('pt-BR') : '-'}</span>
                            </div>
                            <div className="text-right">
                                <span className="text-gray-400 block">Vigência Final</span>
                                <span className={`font-medium ${p.status === 'Ativo' ? 'text-green-600' : 'text-red-600'}`}>
                                    {p.vigencia_final ? new Date(p.vigencia_final.seconds*1000).toLocaleDateString('pt-BR') : '-'}
                                </span>
                            </div>
                        </div>
                        
                        {p.financeiro && (
                             <div className="mt-2 pt-2 border-t border-dashed text-xs flex justify-between">
                                <span>Franquia: R$ {p.financeiro.franquia?.toFixed(2)}</span>
                                <span className="font-bold">Prêmio: R$ {p.financeiro.premio_total?.toFixed(2)}</span>
                             </div>
                        )}
                        </Card>
                    ))
                    )
                )}
            </div>
        )}
      </div>

      {!isEditing && (
        <div className="p-4 bg-white border-t safe-area-bottom">
            <a href={`https://wa.me/55${(client.telefones || '').replace(/\D/g,'')}`} target="_blank" className="bg-[#25D366] text-white w-full py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg">WhatsApp</a>
        </div>
      )}
    </div>
  );
};"""
}

def populate_files():
    print("--- Atualizando Servidor com Auto-Install (Corrigido) ---")
    current_dir = os.getcwd()
    for relative_path, content in files_content.items():
        file_path = os.path.join(current_dir, relative_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Arquivo atualizado: {relative_path}")

if __name__ == "__main__":
    populate_files()
    print("\\n⚠️ TENTE AGORA:")
    print("1. Rode: python populate_files.py")
    print("2. Pare o servidor python anterior (Ctrl+C).")
    print("3. Inicie: python api_server.py")