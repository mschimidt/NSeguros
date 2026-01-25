import os

# Atualiza apenas o ClientList.jsx para carregar até 5000 clientes e ordenar por nome
client_list_code = """import React, { useState, useMemo, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Shield, LogOut, Search, ChevronRight, Plus, RefreshCw } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { ClientDetail } from './ClientDetail';
import { db } from '../services/firebase';
import { collection, query, limit, getDocs, orderBy, addDoc, serverTimestamp } from 'firebase/firestore';

export const ClientList = () => {
  const { logout, isDemoMode } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClient, setSelectedClient] = useState(null);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const fetchClients = async () => {
      if (isDemoMode) {
          setClients([{ id: '1', nome: 'Cliente Demo', cidade: 'Teste' }]);
          setLoading(false);
          return;
      }

      setLoading(true);
      try {
        // ATUALIZAÇÃO: Limite aumentado para 5000 e ordenação alfabética
        // Isso garante que a busca local funcione em toda a base
        const q = query(
            collection(db, "dim_clientes"), 
            orderBy("nome"), 
            limit(5000)
        );
        
        const snap = await getDocs(q);
        const list = snap.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        setClients(list);
      } catch (e) {
        console.error("Erro ao buscar clientes:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchClients();
  }, [isDemoMode, refreshKey]);

  const handleCreateNew = async () => {
      if(isDemoMode) return alert("Demo Mode");
      const nome = prompt("Nome do cliente:");
      if (!nome) return;
      try {
          await addDoc(collection(db, "dim_clientes"), {
              nome: nome,
              data_cadastro: serverTimestamp(),
              search_keywords: nome.toLowerCase().split(' ')
          });
          setRefreshKey(p => p + 1);
      } catch(e) { alert(e.message); }
  };

  const filteredClients = useMemo(() => {
    if (!searchTerm) return clients;
    const lower = searchTerm.toLowerCase();
    
    // Busca inteligente em múltiplos campos
    return clients.filter(c => 
      (c.nome && c.nome.toLowerCase().includes(lower)) || 
      (c.cpf_cnpj && c.cpf_cnpj.includes(lower)) ||
      (c.cidade && c.cidade.toLowerCase().includes(lower)) ||
      (c.telefones && c.telefones.includes(lower))
    );
  }, [searchTerm, clients]);

  return (
    <div className="min-h-screen bg-slate-50 pb-20 font-sans text-gray-900">
      <header className="bg-blue-600 text-white p-4 pt-4 sticky top-0 z-30 shadow-md">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-2">
            <Shield size={20} />
            <h1 className="font-bold text-lg">Carteira</h1>
          </div>
          <button onClick={logout}><LogOut size={20} /></button>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-2.5 text-blue-200" size={18} />
          <input 
            className="w-full bg-blue-700/50 text-white placeholder-blue-200 rounded-xl py-2 pl-10 pr-4 outline-none focus:bg-white focus:text-gray-900 transition-colors"
            placeholder="Buscar por nome, CPF, cidade..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
        </div>
      </header>

      <main className="p-4 space-y-3">
        <div className="flex justify-between px-1 text-sm text-gray-500">
          <span>
             {loading ? 'Carregando base...' : `${filteredClients.length} clientes exibidos`}
             {!loading && clients.length >= 5000 && <span className="text-orange-500 ml-1">(Limite atingido)</span>}
          </span>
          <button onClick={() => setRefreshKey(p => p+1)} className="text-blue-600 flex items-center gap-1">
            <RefreshCw size={14}/> Atualizar
          </button>
        </div>

        {loading ? (
            <div className="flex flex-col items-center py-12 gap-3">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="text-gray-400 text-sm">Sincronizando clientes...</p>
            </div>
        ) : filteredClients.map(client => (
          <Card key={client.id} onClick={() => setSelectedClient(client)} className="flex justify-between items-center cursor-pointer hover:border-blue-300 transition-colors">
            <div className="flex gap-3 overflow-hidden items-center">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs shrink-0 uppercase">
                {client.nome ? client.nome.substring(0,2) : '??'}
              </div>
              <div>
                <h3 className="font-bold text-gray-800 truncate text-sm">{client.nome}</h3>
                <p className="text-xs text-gray-500 flex gap-2">
                    <span>{client.cidade || 'N/A'}</span>
                    {client.telefones && <span className="text-blue-400">• {client.telefones.split(',')[0]}</span>}
                </p>
              </div>
            </div>
            <ChevronRight size={18} className="text-gray-300" />
          </Card>
        ))}
        
        {!loading && filteredClients.length === 0 && (
            <div className="text-center py-10 text-gray-400">
                Nenhum cliente encontrado para "{searchTerm}"
            </div>
        )}
      </main>

      {selectedClient && (
        <ClientDetail 
          client={selectedClient} 
          onClose={() => setSelectedClient(null)} 
          onUpdate={() => setRefreshKey(p => p + 1)}
        />
      )}
      
      <button onClick={handleCreateNew} className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 rounded-full shadow-lg text-white flex items-center justify-center active:scale-95 transition-transform z-40">
        <Plus size={24} />
      </button>
    </div>
  );
};
"""

file_path = "src/pages/ClientList.jsx"
os.makedirs(os.path.dirname(file_path), exist_ok=True)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(client_list_code)

print(f"✅ Arquivo '{file_path}' atualizado!")
print("🚀 Limite de clientes aumentado para 5000. Recarregue a página do App.")