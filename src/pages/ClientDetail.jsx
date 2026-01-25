import React, { useState, useEffect } from 'react';
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
};