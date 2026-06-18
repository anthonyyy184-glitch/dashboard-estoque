import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página Web com pegada Cyberpunk/Futurista
st.set_page_config(page_title="🎯 NEXUS BI - Controle de Estoque", layout="wide")

# Título estilizado (Usa HTML para dar um toque de cor neon)
st.markdown("<h1 style='text-align: center; color: #00F0FF; font-family: Ubuntu, sans-serif;'>🌌 NEXUS OPERATIONS - BUSINESS INTELLIGENCE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8892B0;'>Monitoramento Preditivo e Fluxo de Estoque em Tempo Real</p>", unsafe_allow_html=True)
st.markdown("---")

# --- BARRA LATERAL FUTURISTA ---
st.sidebar.markdown("<h2 style='color: #00F0FF;'>🛸 CONTROL PANEL</h2>", unsafe_allow_html=True)
arquivo_subido = st.sidebar.file_uploader("📥 Upload New Data Stream (.csv ou .xlsx)", type=["csv", "xlsx"])

# Lógica de carregamento de dados
if arquivo_subido is not None:
    try:
        if arquivo_subido.name.endswith('.csv'):
            df = pd.read_csv(arquivo_subido)
        else:
            df = pd.read_excel(arquivo_subido)
        st.sidebar.success("⚡ Data Sync: COMPLETED")
    except Exception as e:
        st.sidebar.error(f"⚠️ Sync Error: {e}")
        df = pd.read_csv("Base_Tabular_SQL.csv")
else:
    df = pd.read_csv("Base_Tabular_SQL.csv")

# --- TRATAMENTO OPERACIONAL ---
df["Entrada"] = pd.to_numeric(df["Entrada"], errors='coerce').fillna(0)
df["Saída"] = pd.to_numeric(df["Saída"], errors='coerce').fillna(0)
df["Data_Tratada"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors='coerce')
df["Ano_Mes"] = df["Data_Tratada"].dt.to_period("M").astype(str)

# --- FILTROS ---
categorias = ["TODAS AS CULTURAS"] + list(df["Categoria"].dropna().unique())
cat_sel = st.sidebar.selectbox("🎯 Isolar Categoria:", categorias)

if cat_sel != "TODAS AS CULTURAS":
    df = df[df["Categoria"] == cat_sel]

# --- CÁLCULO DOS KPIS ---
total_entradas = df["Entrada"].sum()
total_saidas = df["Saída"].sum()
saldo_estoque = total_entradas - total_saidas

# Mostra os Cards com destaque visual
col1, col2, col3 = st.columns(3)
col1.metric("⚡ INPUT TOTAL (KG)", f"{total_entradas:,.0f}".replace(",", "."))
col2.metric("🚀 OUTPUT TOTAL (KG)", f"{total_saidas:,.0f}".replace(",", "."))
col3.metric("🛸 CURRENT STOCK (KG)", f"{saldo_estoque:,.0f}".replace(",", "."), 
            delta="ESTÁVEL" if saldo_estoque >= 0 else "CRÍTICO", delta_color="normal" if saldo_estoque >= 0 else "inverse")

st.markdown("---")

# --- CRIAÇÃO DAS ABAS ESTILO APP ---
aba_dashboard, aba_tabela = st.tabs(["📊 VISUAL INTELLIGENCE", "🗃️ MATRIX DATA"])

with aba_dashboard:
    # 1. Gráfico de Rosca (Cores Neon/Elétricas)
    df_contagem = df["Categoria"].value_counts().reset_index()
    df_contagem.columns = ["Categoria", "Quantidade de Registros"]
    fig_rosca = px.pie(df_contagem, names="Categoria", values="Quantidade de Registros", hole=0.6, 
                       color_discrete_sequence=px.colors.sequential.Ice_r) # Paleta de azuis/cianos elétricos
    fig_rosca.update_traces(textposition='inside', textinfo='percent+label')
    fig_rosca.update_layout(title="📦 Volume de Operações por Categoria", template="plotly_dark")

    # 2. Gráfico de Barras (Top Produtores)
    top_produtores = df.groupby("Produtor")["Entrada"].sum().reset_index()
    top_produtores = top_produtores[~top_produtores["Produtor"].str.lower().str.contains("estoque|fato", na=True)]
    top_produtores = top_produtores.sort_values(by="Entrada", ascending=False).head(5)
    fig_barras = px.bar(top_produtores, x="Entrada", y="Produtor", orientation='h', 
                        color="Entrada", color_continuous_scale="Electric") # Degradê neon sensacional
    fig_barras.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False, 
                             title="🥇 Top 5 Fornecedores Líderes (Kg)", template="plotly_dark")

    # 3. Gráfico de Linhas (Evolução Temporal)
    df_temporal = df[df["Ano_Mes"] != "NaT"].groupby("Ano_Mes")[["Entrada", "Saída"]].sum().reset_index().sort_values("Ano_Mes")
    fig_linha = go.Figure()
    # Linha Verde Neon para Entradas
    fig_linha.add_trace(go.Scatter(x=df_temporal["Ano_Mes"], y=df_temporal["Entrada"], mode='lines+markers', 
                                   name='Inputs (Kg)', line=dict(color='#00FF66', width=4)))
    # Linha Rosa/Roxa Neon para Saídas
    fig_linha.add_trace(go.Scatter(x=df_temporal["Ano_Mes"], y=df_temporal["Saída"], mode='lines+markers', 
                                   name='Outputs (Kg)', line=dict(color='#FF007F', width=4)))
    fig_linha.update_layout(title="📈 Linha de Tendência Temporal (Fluxo de Carga)", template="plotly_dark",
                            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))

    # Renderiza os gráficos soltos na tela (Eles se adaptam perfeitamente ao celular e ao PC automaticamente!)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_rosca, use_container_width=True)
    with c2:
        st.plotly_chart(fig_barras, use_container_width=True)
        
    st.markdown("---")
    st.plotly_chart(fig_linha, use_container_width=True)

with aba_tabela:
    st.markdown("<h3 style='color: #00F0FF;'>📋 Banco de Dados Consolidado</h3>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)
