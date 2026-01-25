import React, { useState, useMemo, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Search, ChevronRight, Plus, RefreshCw } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { ClientDetail } from './ClientDetail';
import { Navbar } from '../components/layout/Navbar';
import { db } from '../services/firebase';
import { collection, query, limit, getDocs, orderBy, addDoc, serverTimestamp, doc, getDoc } from 'firebase/firestore';

export const ClientList = () => {
  const { isDemoMode } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClient, setSelectedClient] = useState(null);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  // Efeito para carregar cliente vindo de outra tela (ex: Seguros a Vencer)
  useEffect(() => {
      const openClientFromState = async () => {
        if (location.state?.openClientId) {
            const clientId = location.state.openClientId;
            // Limpa o state para não reabrir ao dar refresh
            window.history.replaceState({}, document.title);
            
            // Tenta achar na lista atual
            const found = clients.find(c => c.id === clientId);
            if (found) {
                setSelectedClient(found);
            } else {
                // Se não estiver carregado na lista (ex: lista limitada), busca individual
                try {
                    const docRef = doc(db, "dim_clientes", clientId);
                    const docSnap = await getDoc(docRef);
                    if (docSnap.exists()) {
                        const clientData = { id: docSnap.id, ...docSnap.data() };
                        setSelectedClient(clientData);
                    }
                } catch (e) {
                    console.error("Erro ao carregar cliente específico", e);
                }
            }
        }
      };
      
      if (!loading) openClientFromState();
  }, [location.state, loading, clients]);

  useEffect(() => {
    const fetchClients = async () => {
      if (isDemoMode) {
          setClients([{ id: '1', nome: 'Cliente Demo', cidade: 'Teste' }]);
          setLoading(false);
          return;
      }

      setLoading(true);
      try {
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
    return clients.filter(c => 
      (c.nome && c.nome.toLowerCase().includes(lower)) || 
      (c.cpf_cnpj && c.cpf_cnpj.includes(lower)) ||
      (c.cidade && c.cidade.toLowerCase().includes(lower)) ||
      (c.telefones && c.telefones.includes(lower))
    );
  }, [searchTerm, clients]);

  return (
    <div className="min-h-screen bg-slate-50 pb-20 font-sans text-gray-900">
      <Navbar />

      {/* Sub-header de Busca (separado do Navbar para limpeza) */}
      <div className="bg-white p-3 shadow-sm border-b sticky top-[72px] z-30">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          <input 
            className="w-full bg-gray-100 text-gray-900 rounded-xl py-2 pl-10 pr-4 outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            placeholder="Buscar clientes..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <main className="p-4 space-y-3">
        <div className="flex justify-between px-1 text-sm text-gray-500">
          <span>{filteredClients.length} clientes</span>
          <button onClick={() => setRefreshKey(p => p+1)} className="text-blue-600 flex items-center gap-1">
            <RefreshCw size={14}/> 
          </button>
        </div>

        {loading ? (
            <div className="text-center py-10 text-gray-400">Carregando carteira...</div>
        ) : filteredClients.map(client => (
          <Card key={client.id} onClick={() => setSelectedClient(client)} className="flex justify-between items-center cursor-pointer hover:border-blue-300 transition-colors">
            <div className="flex gap-3 overflow-hidden items-center">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs shrink-0 uppercase">
                {client.nome ? client.nome.substring(0,2) : '??'}
              </div>
              <div>
                <h3 className="font-bold text-gray-800 truncate text-sm">{client.nome}</h3>
                <p className="text-xs text-gray-500 flex gap-2">
                    <span className="truncate max-w-[150px]">{client.cidade || 'N/A'}</span>
                </p>
              </div>
            </div>
            <ChevronRight size={18} className="text-gray-300" />
          </Card>
        ))}
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