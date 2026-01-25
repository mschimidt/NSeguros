import React, { useState, useEffect } from 'react';
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
};