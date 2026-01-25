import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os
import numpy as np

# --- CONFIGURAÇÃO ---
cred_path = 'serviceAccountKey.json'

def init_firebase():
    if not firebase_admin._apps:
        try:
            if not os.path.exists(cred_path):
                print("❌ ERRO: 'serviceAccountKey.json' não encontrado.")
                return False
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase conectado.")
            return True
        except Exception as e:
            print(f"❌ Erro conexão: {e}")
            return False
    return True

db = None 

# --- HELPERS DE LIMPEZA ---
def load_data(table_name):
    """Carrega dados tentando CSV e depois Excel"""
    csv_name = f"DADOS.xls - {table_name}.csv"
    if os.path.exists(csv_name):
        print(f"📖 Lendo {csv_name}...")
        try: return pd.read_csv(csv_name)
        except Exception as e: print(f"⚠️ Erro CSV: {e}")
            
    xls_name = "DADOS.xls"
    if os.path.exists(xls_name):
        print(f"📖 Lendo aba '{table_name}' do Excel...")
        try: return pd.read_excel(xls_name, sheet_name=table_name)
        except Exception as e: print(f"⚠️ Erro Excel: {e}")
    return None

def clean_str(val):
    if pd.isna(val) or str(val).strip() == 'nan': return ""
    return str(val).strip()

def clean_int(val):
    if pd.isna(val): return 0
    try: return int(float(val))
    except: return 0

def clean_float(val):
    if pd.isna(val): return 0.0
    try: return float(val)
    except: return 0.0

def clean_date(val):
    if pd.isna(val) or str(val).strip() == '': return None
    try: return pd.to_datetime(val)
    except: return None

# --- MIGRAÇÃO DE DIMENSÕES ---

def migrate_dim_generic(df, collection, id_field, name_field, extra_fields=[]):
    if df is None: return {}
    print(f">>> Migrando {collection}...")
    batch = db.batch()
    count = 0
    lookup = {} 
    
    for _, row in df.iterrows():
        doc_id = str(row[id_field])
        name = clean_str(row[name_field])
        lookup[doc_id] = name
        
        data = {
            'id': clean_int(row[id_field]),
            'descricao': name,
            'search_key': name.lower()
        }
        
        for field in extra_fields:
            if field in row:
                data[field] = clean_str(row[field])
        
        ref = db.collection(collection).document(doc_id)
        batch.set(ref, data)
        count += 1
        if count >= 400:
            batch.commit(); batch = db.batch(); count = 0
            
    if count > 0: batch.commit()
    return lookup

def migrate_clientes():
    df = load_data('clientes')
    if df is None: return {}
    print(">>> Migrando dim_clientes (COMPLETO)...")
    
    batch = db.batch()
    count = 0
    lookup = {}

    for _, row in df.iterrows():
        doc_id = str(row['codigo'])
        nome = clean_str(row['nome']).title()
        lookup[doc_id] = nome
        
        # Mapeamento Completo de Campos
        data = {
            'legacy_id': clean_int(row['codigo']),
            'nome': nome,
            'search_keywords': nome.lower().split(),
            'data_cadastro': clean_date(row['datadoc']),
            
            # Documentos
            'cpf_cnpj': clean_str(row['cpf']) if clean_str(row['cpf']) else clean_str(row['cnpj']),
            'rg': clean_str(row['numdoc']), # Assumindo numdoc como RG baseado no snippet
            'orgao_emissor': clean_str(row['orgaodoc']),
            'cnh': clean_str(row['cnh']),
            'cnh_validade': clean_date(row['validade']) if 'validade' in row else None,
            
            # Pessoal
            'nascimento': clean_date(row['nascimento']),
            'sexo': clean_str(row['sexo']),
            'estado_civil': clean_str(row['ecivil']),
            'profissao': clean_str(row['profissao']),
            'tipo_pessoa': clean_str(row['pessoa']), # F ou J
            
            # Contato
            'email': clean_str(row['email']).lower(),
            'telefones': clean_str(row['fones']),
            
            # Endereço Residencial
            'endereco': clean_str(row['endereco']),
            'bairro': clean_str(row['bairro']),
            'cidade': clean_str(row['cidade']),
            'uf': clean_str(row['estado']),
            'cep': clean_str(row['cep']),
            
            # Endereço Comercial/Outro (Campos com prefixo 'o')
            'end_comercial': clean_str(row['oendereco']),
            'bairro_comercial': clean_str(row['obairro']),
            'cidade_comercial': clean_str(row['ocidade']),
            'uf_comercial': clean_str(row['oestado']),
            'cep_comercial': clean_str(row['ocep']),
            
            # Extras
            'obs': clean_str(row['obs'])
        }
        
        # Remove campos vazios para limpar o banco
        data = {k: v for k, v in data.items() if v != "" and v is not None}
        
        ref = db.collection('dim_clientes').document(doc_id)
        batch.set(ref, data)
        count += 1
        if count >= 400:
            batch.commit(); batch = db.batch(); count = 0
            
    if count > 0: batch.commit()
    return lookup

def migrate_fact_seguros(map_cli, map_prod, map_ramo, map_marca, map_seg):
    df = load_data('seguros')
    if df is None: return
    print(">>> Migrando fact_seguros (COMPLETO)...")
    
    batch = db.batch()
    count = 0
    
    for _, row in df.iterrows():
        doc_id = str(row['codigo'])
        
        # Foreign Keys
        fk_cli = str(row['cliente'])
        fk_prod = str(row['produtor'])
        fk_ramo = str(row['ramo'])
        fk_marca = str(clean_int(row['marca']))
        fk_seg = str(row['seguradora'])
        
        data = {
            'legacy_id': clean_int(row['codigo']),
            'status': 'Ativo' if str(row['ativo']) == '1' else 'Inativo',
            
            # Relacionamentos
            'fk_cliente': fk_cli,
            'fk_produtor': fk_prod,
            'fk_ramo': fk_ramo,
            'fk_marca': fk_marca,
            'fk_seguradora': fk_seg,
            
            # Lookup Names (Para performance)
            'dim_cliente_nome': map_cli.get(fk_cli, "Desconhecido"),
            'dim_produtor_nome': map_prod.get(fk_prod, "Desconhecido"),
            'dim_ramo_nome': map_ramo.get(fk_ramo, "Outros"),
            'dim_marca_nome': map_marca.get(fk_marca, "Outra"),
            'dim_seguradora_nome': map_seg.get(fk_seg, "Outra"),
            
            # Dados da Apólice
            'apolice': clean_str(row['apolice']),
            'proposta': clean_str(row['proposta']),
            'item': clean_str(row['item']),
            'ci': clean_str(row['ci']), # Código de Identificação
            'classe_bonus': clean_str(row['bonus']),
            'vigencia_inicio': clean_date(row['inicio']),
            'vigencia_final': clean_date(row['final']),
            'data_emissao': clean_date(row['dtsaida']),
            
            # Veículo Detalhado
            'veiculo': {
                'modelo': clean_str(row['modelo']),
                'placa': clean_str(row['placa']).upper(),
                'chassi': clean_str(row['chassi']),
                'renavam': clean_str(row['renavam']),
                'cor': clean_str(row['cor']),
                'ano_fab': clean_int(row['anofab']),
                'ano_mod': clean_int(row['anomod']),
                'portas': clean_int(row['portas']),
                'zero_km': True if str(row['zero']) == '1' else False,
                'kit_gas': True if str(row['kitgas']) == '1' else False
            },
            
            # Coberturas e Valores
            'financeiro': {
                'premio_total': clean_float(row['valornf']),
                'importancia_segurada': clean_float(row['is']), # IS Casco
                'franquia': clean_float(row['franquia']),
                'danos_materiais': clean_float(row['dm']),
                'danos_corporais': clean_float(row['dc']),
                'danos_morais': clean_float(row['dmorais']),
                'app_morte': clean_float(row['appmorte']),
                'app_invalidez': clean_float(row['appinv'])
            },
            
            'obs': clean_str(row['obs'])
        }
        
        # Limpeza Profunda de dicts aninhados vazios
        data = {k: v for k, v in data.items() if v != "" and v is not None}
        
        ref = db.collection('fact_seguros').document(doc_id)
        batch.set(ref, data)
        count += 1
        if count >= 400:
            batch.commit(); batch = db.batch(); count = 0
            
    if count > 0: batch.commit()
    print("✅ Fatos Migrados!")

def run():
    global db
    if not init_firebase(): return
    db = firestore.client()
    
    # 1. Dimensões
    map_cli = migrate_clientes()
    
    df_prod = load_data('produtores')
    map_prod = migrate_dim_generic(df_prod, 'dim_produtores', 'codigo', 'nome', ['cpf', 'cnpj'])
    
    df_ramos = load_data('ramos')
    map_ramo = migrate_dim_generic(df_ramos, 'dim_ramos', 'codigo', 'ramo')
    
    df_marcas = load_data('marcas')
    map_marca = migrate_dim_generic(df_marcas, 'dim_marcas', 'codigo', 'nome')
    
    df_seg = load_data('seguradoras')
    map_seg = migrate_dim_generic(df_seg, 'dim_seguradoras', 'codigo', 'nome')
    
    df_cob = load_data('coberturas')
    migrate_dim_generic(df_cob, 'dim_coberturas', 'codigo', 'descricao', ['ramo'])

    df_lic = load_data('licencia')
    if df_lic is not None:
        print(">>> Migrando dim_licencia...")
        b = db.batch()
        for _, r in df_lic.iterrows():
            ref = db.collection('dim_licencia').document(str(r['final']))
            b.set(ref, {
                'final': clean_int(r['final']), 
                'veiculo': clean_int(r['veiculo']), 
                'caminhao': clean_int(r['caminhao'])
            })
        b.commit()

    # 2. Fatos
    migrate_fact_seguros(map_cli, map_prod, map_ramo, map_marca, map_seg)
    print("🚀 ETL Completo com Sucesso!")

if __name__ == '__main__':
    run()