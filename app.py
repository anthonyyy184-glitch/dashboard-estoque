import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página Web (Modo Amplo)
st.set_page_config(page_title="Dashboard de Estoque", layout="wide")

# Título limpo e profissional
st.markdown("<h1 style='text-align: center; color: #FFFFFF; font-family: Arial, sans-serif;'>📊 Painel de Controle de Estoque</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9A9A9A;'>Gestão de Movimentações, Entradas e Saídas de Culturas</p>", unsafe_allow_html=True)
st.markdown("---")

# --- BARRA LATERAL OPERACIONAL ---
st.sidebar.markdown("<h2 style='color: #FFFFFF;'>🔄 Gestão de Dados</h2>", unsafe_allow_html=True)
arquivo_subido = st.sidebar.file_uploader("📥 Atualizar Base de Dados (.csv ou .xlsx)", type=["csv", "xlsx"])

# Lógica de carregamento de dados
if arquivo_subido is not None:
    try:
        if arquivo_subido.name.endswith('.csv'):
            df = pd.read_csv(arquivo_subido)
        else:
            df = pd.read_excel(arquivo_subido)
        st.sidebar.success("Dados atualizados!")
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar dados: {e}")
        df = pd.read_csv("Base_Tabular_SQL.csv")
else:
    df = pd.read_csv("Base_Tabular_SQL.csv")

# --- TRATAMENTO DOS DADOS ---
df["Entrada"] = pd.to_numeric(df["Entrada"], errors='coerce').fillna(0)
df["Saída"] = pd.to_numeric(df["Saída"], errors='coerce').fillna(0)
df["Data_Tratada"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors='coerce')
df["Ano_Mes"] = df["Data_Tratada"].dt.to_period("M").astype(str)

# --- FILTRO SIMPLES ---
categorias = ["Todas as Categorias"] + list(df["Categoria"].dropna().unique())
cat_sel = st.sidebar.selectbox("🎯 Filtrar por Categoria:", categorias)

if cat_sel != "Todas as Categorias":
    df = df[df["Categoria"] == cat_sel]

# --- RESUMO DOS KPIS ---
total_entradas = df["Entrada"].sum()
total_saidas = df["Saída"].sum()
saldo_estoque = total_entradas - total_saidas

# Cards de destaque objetivos
col1, col2, col3 = st.columns(3)
col1.metric("📦 ENTRADAS TOTAIS (KG)", f"{total_entradas:,.0f}".replace(",", "."))
col2.metric("🚚 SAÍDAS TOTAIS (KG)", f"{total_saidas:,.0f}".replace(",", "."))
col3.metric("⚖️ SALDO EM ESTOQUE (KG)", f"{saldo_estoque:,.0f}".replace(",", "."), 
            delta="ESTOQUE DISPONÍVEL" if saldo_estoque >= 0 else "ESTOQUE NEGATIVO", delta_color="normal" if saldo_estoque >= 0 else "inverse")

st.markdown("---")

# --- ABAS DE NAVEGAÇÃO COMPATÍVEIS COM CELULAR ---
aba_graficos, aba_tabela = st.tabs(["📊 Visão Geral do Painel", "📋 Tabela de Dados Brutos"])

with aba_graficos:
    # 1. Gráfico de Rosca (Cores Limpas e Modernas)
    df_contagem = df["Categoria"].value_counts().reset_index()
    df_contagem.columns = ["Categoria", "Quantidade de Registros"]
    fig_rosca = px.pie(df_contagem, names="Categoria", values="Quantidade de Registros", hole=0.5, 
                       color_discrete_sequence=px.colors.qualitative.T10) # Cores sólidas e corporativas
    fig_rosca.update_traces(textposition='inside', textinfo='percent+label')
    fig_rosca.update_layout(title="Volume de Movimentações por Categoria", template="plotly_dark")

    # 2. Gráfico de Barras (Top Fornecedores)
    top_produtores = df.groupby("Produtor")["Entrada"].sum().reset_index()
    top_produtores = top_produtores[~top_produtores["Produtor"].str.lower().str.contains("estoque|fato", na=True)]
    top_produtores = top_produtores.sort_values(by="Entrada", ascending=False).head(5)
    fig_barras = px.bar(top_produtores, x="Entrada", y="Produtor", orientation='h', 
                        color="Entrada", color_continuous_scale="Blues") # Degradê de azul bem elegante
    fig_barras.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False, 
                             title="Top 5 Fornecedores Líderes (Kg)", template="plotly_dark")

    # 3. Gráfico de Linhas (Evolução Temporal)
    df_temporal = df[df["Ano_Mes"] != "NaT"].groupby("Ano_Mes")[["Entrada", "Saída"]].sum().reset_index().sort_values("Ano_Mes")
    fig_linha = go.Figure()
    # Linha Verde para Entradas
    fig_linha.add_trace(go.Scatter(x=df_temporal["Ano_Mes"], y=df_temporal["Entrada"], mode='lines+markers', 
                                   name='Entradas (Kg)', line=dict(color='#2ECC71', width=3)))
    # Linha Vermelha para Saídas
    fig_linha.add_trace(go.Scatter(x=df_temporal["Ano_Mes"], y=df_temporal["Saída"], mode='lines+markers', 
                                   name='Saídas (Kg)', line=dict(color='#E74C3C', width=3)))
    fig_linha.update_layout(title="Evolução Mensal (Fluxo de Carga)", template="plotly_dark",
                            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))

    # Renderização responsiva (lado a lado no PC, empilhado no celular)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_rosca, use_container_width=True)
    with c2:
        st.plotly_chart(fig_barras, use_container_width=True)
        
    st.markdown("---")
    st.plotly_chart(fig_linha, use_container_width=True)

with aba_tabela:
    st.markdown("<h3 style='color: #FFFFFF;'>📋 Dados Consolidados</h3>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)
