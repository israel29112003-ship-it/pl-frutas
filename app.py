import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# 1. CONEXÃO SEGURA COM O GOOGLE SHEETS
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Puxa as chaves direto do Secrets que você configurou
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    # Abre a planilha (Certifique-se que o nome está idêntico: BD_PL_Frutas)
    return client.open("BD_PL_Frutas").sheet1

st.set_page_config(page_title="PL Frutas PRO", layout="wide")
st.title("🚜 PL Frutas - Gestão Profissional")

# --- FORMULÁRIO DE ENTRADA ---
with st.expander("📝 LANÇAR NOVA DESPESA", expanded=True):
    with st.form("registro_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        data_f = col1.date_input("Data", date.today())
        lote_f = col2.selectbox("Lote", ["Lote de Coco", "Lote de Melancia", "Lote de Milho", "Lote de Banana"])
        cat_f = col1.selectbox("Categoria", ["Insumo", "Mão de Obra", "Combustível", "Manutenção", "Outros"])
        desc_f = col2.text_input("Descrição (Ex: Adubo NPK)")
        val_f = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
        
        btn = st.form_submit_button("SALVAR NA NUVEM")

        if btn:
            try:
                aba = conectar()
                # Salva na planilha: data, lote, categoria, descricao, valor
                aba.append_row([str(data_f), lote_f, cat_f, desc_f, val_f])
                st.success("✅ Gasto registrado com sucesso no Google Sheets!")
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# --- DASHBOARD EM TEMPO REAL ---
st.markdown("---")
try:
    aba = conectar()
    dados = aba.get_all_records()
    if dados:
        df = pd.DataFrame(dados)
        # Força o valor a ser número
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💰 Resumo Financeiro por Lote")
            resumo = df.groupby('lote')['valor'].sum()
            st.bar_chart(resumo)
        with c2:
            st.subheader("📋 Últimos 5 Lançamentos")
            st.dataframe(df.tail(5), use_container_width=True)
    else:
        st.info("A planilha está vazia. Faça o primeiro lançamento acima!")
except Exception as e:
    st.warning("Aguardando conexão ou dados da planilha...")
