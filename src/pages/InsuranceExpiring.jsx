import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { collection, query, where, getDocs, orderBy, Timestamp } from 'firebase/firestore';
import { db } from '../services/firebase';
import { useAuth } from '../contexts/AuthContext';
import { Navbar } from '../components/layout/Navbar';
import { Card } from '../components/ui/Card';
import { Calendar, Car, AlertCircle, ChevronRight } from 'lucide-react';

export const InsuranceExpiring = () => {
  const { isDemoMode } = useAuth();
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchExpiring = async () => {
      setLoading(true);
      if (isDemoMode) {
        // Mock
        setPolicies([{
            id: 'demo1', 
            dim_cliente_nome: 'Cliente Demo', 
            dim_seguradora_nome: 'Porto Seguro',
            veiculo_modelo: 'Fusca 1980',
            vigencia_final: { seconds: Date.now()/1000 + 86400 * 5 }, // +5 dias
            fk_cliente: '1'
        }]);
        setLoading(false);
        return;
      }

      try {
        // Data de hoje e hoje + 30 dias
        const today = new Date();
        const thirtyDaysLater = new Date();
        thirtyDaysLater.setDate(today.getDate() + 30);

        // Firestore Query
        // Nota: Filtros de desigualdade em múltiplos campos podem exigir índice.
        // Vamos filtrar 'Ativo' e Data no cliente para garantir funcionamento sem erro de índice complexo.
        const q = query(
          collection(db, "fact_seguros"),
          where("status", "==", "Ativo"),
          orderBy("vigencia_final") 
        );

        const snap = await getDocs(q);
        
        // Filtra os próximos 30 dias em memória (mais seguro sem criar índices manuais agora)
        const expiringList = snap.docs
          .map(doc => ({ id: doc.id, ...doc.data() }))
          .filter(p => {
            if (!p.vigencia_final) return false;
            const vDate = new Date(p.vigencia_final.seconds * 1000);
            return vDate >= today && vDate <= thirtyDaysLater;
          });

        setPolicies(expiringList);

      } catch (e) {
        console.error("Erro ao buscar seguros:", e);
      } finally {
        setLoading(false);
      }
    };

    fetchExpiring();
  }, [isDemoMode]);

  const handleOpenPolicy = (policy) => {
    // Navega para a Home (Lista de Clientes) e pede para abrir este cliente específico
    navigate('/', { state: { openClientId: policy.fk_cliente } });
  };

  return (
    <div className="min-h-screen bg-slate-50 pb-20 font-sans text-gray-900">
      <Navbar />

      <main className="p-4 space-y-3">
        {loading ? (
            <div className="text-center py-10 flex flex-col items-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mb-2"></div>
                <p className="text-gray-400 text-sm">Buscando vencimentos...</p>
            </div>
        ) : (
            <>
                <div className="px-1 py-2 text-sm font-medium text-gray-500 flex items-center gap-2">
                    <AlertCircle size={16} className="text-orange-500" />
                    {policies.length} apólices vencendo em 30 dias
                </div>

                {policies.length === 0 ? (
                    <div className="text-center py-12 text-gray-400 bg-white rounded-xl border border-dashed">
                        <Calendar size={48} className="mx-auto mb-2 opacity-20" />
                        <p>Nenhum seguro vencendo próximo.</p>
                    </div>
                ) : (
                    policies.map(p => {
                        const daysLeft = Math.ceil((new Date(p.vigencia_final.seconds * 1000) - new Date()) / (1000 * 60 * 60 * 24));
                        return (
                            <Card 
                                key={p.id} 
                                onClick={() => handleOpenPolicy(p)}
                                className="cursor-pointer border-l-4 border-l-orange-500 hover:bg-orange-50/30 transition-colors"
                            >
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded uppercase">
                                        {p.dim_ramo_nome || 'Seguro'}
                                    </span>
                                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${daysLeft <= 7 ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
                                        Vence em {daysLeft} dias
                                    </span>
                                </div>
                                <h3 className="font-bold text-gray-800 text-base">{p.dim_cliente_nome}</h3>
                                <div className="text-sm text-gray-600 mb-2">{p.dim_seguradora_nome}</div>
                                
                                {p.veiculo_modelo && (
                                    <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-50 p-2 rounded">
                                        <Car size={14} />
                                        <span className="truncate">{p.veiculo_modelo}</span>
                                        <span className="font-mono bg-white px-1 rounded border">{p.veiculo_placa}</span>
                                    </div>
                                )}
                                
                                <div className="mt-2 pt-2 border-t flex justify-between items-center text-xs text-gray-500">
                                    <span>Vencimento:</span>
                                    <span className="font-bold text-gray-800">
                                        {new Date(p.vigencia_final.seconds * 1000).toLocaleDateString('pt-BR')}
                                    </span>
                                </div>
                            </Card>
                        );
                    })
                )}
            </>
        )}
      </main>
    </div>
  );
};