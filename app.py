import streamlit as st
import pandas as pd

st.set_page_config(page_title="PL Frutas - Gestão Inteligente", page_icon="🚜", layout="wide")

def carregar_dados():
    try:
        estoque = pd.read_csv('estoque.csv', encoding='latin1', sep=None, engine='python')
        financeiro = pd.read_csv('financeiro_lotes.csv', encoding='latin1', sep=None, engine='python')
        
        estoque.columns = estoque.columns.str.strip().str.lower()
        financeiro.columns = financeiro.columns.str.strip().str.lower()

        # --- LIMPEZA AVANÇADA DO VALOR ---
        if 'valor' in financeiro.columns:
            # 1. Transforma tudo em texto
            financeiro['valor'] = financeiro['valor'].astype(str)
            # 2. Remove o "R$", espaços e pontos de milhar
            financeiro['valor'] = financeiro['valor'].str.replace('R$', '', regex=False).str.replace(' ', '')
            # 3. Troca vírgula por ponto para o padrão do Python
            financeiro['valor'] = financeiro['valor'].str.replace(',', '.')
            # 4. Converte para número real
            financeiro['valor'] = pd.to_numeric(financeiro['valor'], errors='coerce').fillna(0)
            
        return estoque, financeiro
    except Exception as e:
        st.error(f"Erro: {e}")
        return None, None

df_estoque, df_financeiro = carregar_dados()

if df_estoque is not None and df_financeiro is not None:
    st.title("🚜 PL Frutas - Gestão de Lotes")
    
    c1, c2 = st.columns(2)
    with c1:
        total = df_financeiro['valor'].sum()
        st.metric("Gasto Total", f"R$ {total:,.2f}")
    
    st.markdown("---")
    st.subheader("💰 Gastos por Lote")
    grafico_dados = df_financeiro.groupby('lote')['valor'].sum()
    st.bar_chart(grafico_dados)
    
    st.subheader("📋 Tabela de Dados")
    st.dataframe(df_financeiro)