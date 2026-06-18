import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Configuração da Página Web
st.set_page_config(page_title="Dashboard BI - Controle de Culturas", layout="wide")

st.title("🏢 Painel Integrado de Business Intelligence")
st.markdown("Gestão de Estoque, Movimentações e Culturas")

# --- BOTÃO DE UPLOAD NA BARRA LATERAL ---
st.sidebar.header("🔄 Atualização de Dados")
arquivo_subido = st.sidebar.file_uploader("Arraste a planilha atualizada aqui (.csv ou .xlsx)", type=["csv", "xlsx"])

# Carrega os dados (Se subir arquivo novo usa ele, se não usa o padrão)
if arquivo_subido is not None:
    try:
        if arquivo_subido.name.endswith('.csv'):
            df = pd.read_csv(arquivo_subido)
        else:
            df = pd.read_excel(arquivo_subido)
        st.sidebar.success("Base atualizada com sucesso!")
    except Exception as e:
        st.sidebar.error(f"Erro ao ler arquivo: {e}")
        df = pd.read_csv("Base_Tabular_SQL.csv")
else:
    df = pd.read_csv("Base_Tabular_SQL.csv")

# --- TRATAMENTO OPERACIONAL ---
df["Entrada"] = pd.to_numeric(df["Entrada"], errors='coerce').fillna(0)
df["Saída"] = pd.to_numeric(df["Saída"], errors='coerce').fillna(0)
df["Data_Tratada"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors='coerce')
df["Ano_Mes"] = df["Data_Tratada"].dt.to_period("M").astype(str)

# --- FILTROS VISUAIS ---
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtros do Painel")
categorias = ["Todas"] + list(df["Categoria"].dropna().unique())
cat_sel = st.sidebar.selectbox("Filtrar por Categoria:", categorias)

if cat_sel != "Todas":
    df = df[df["Categoria"] == cat_sel]

# --- CÁLCULO DOS KPIS ---
total_entradas = df["Entrada"].sum()
total_saidas = df["Saída"].sum()
saldo_estoque = total_entradas - total_saidas

# Exibição dos Cards de KPI
col1, col2, col3 = st.columns(3)
col1.metric("📦 Entradas Totais (Kg)", f"{total_entradas:,.0f}".replace(",", "."))
col2.metric("🚚 Saídas Totais (Kg)", f"{total_saidas:,.0f}".replace(",", "."))
col3.metric("⚖️ Saldo em Estoque (Kg)", f"{saldo_estoque:,.0f}".replace(",", "."))

st.markdown("---")

# --- CONSTRUÇÃO DOS GRÁFICOS ---
# 1. Rosca
df_contagem = df["Categoria"].value_counts().reset_index()
df_contagem.columns = ["Categoria", "Quantidade de Registros"]
fig_rosca = px.pie(df_contagem, names="Categoria", values="Quantidade de Registros", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
fig_rosca.update_traces(textposition='inside', textinfo='percent+label')

# 2. Barras
top_produtores = df.groupby("Produtor")["Entrada"].sum().reset_index()
top_produtores = top_produtores[~top_produtores["Produtor"].str.lower().str.contains("estoque|fato", na=True)]
top_produtores = top_produtores.sort_values(by="Entrada", ascending=False).head(5)
fig_barras = px.bar(top_produtores, x="Entrada", y="Produtor", orientation='h', color="Entrada", color_continuous_scale="Viridis")
fig_barras.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)

# 3. Linhas
df_temporal = df[df["Ano_Mes"] != "NaT"].groupby("Ano_Mes")[["Entrada", "Saída"]].sum().reset_index().sort_values("Ano_Mes")
fig_linha = go.Figure()
fig_linha.add_trace(go.Scatter(x=df_temporal["Ano_Mes"], y=df_temporal["Entrada"], mode='lines+markers', name='Entradas (Kg)', line=dict(color='#2ECC71', width=3)))
fig_linha.add_trace(go.Scatter(x=df_temporal["Ano_Mes"], y=df_temporal["Saída"], mode='lines+markers', name='Saídas (Kg)', line=dict(color='#E74C3C', width=3)))

# Criando o Grid do Dashboard
fig_dashboard = make_subplots(
    rows=2, cols=2,
    specs=[[{"type": "domain"}, {"type": "xy"}], [{"type": "xy", "colspan": 2}, None]],
    subplot_titles=("📦 Movimentações por Categoria", "🥇 Top 5 Produtores (Kg)", "📈 Evolução Temporal (Entradas vs Saídas)")
)

for trace in fig_rosca.data: fig_dashboard.add_trace(trace, row=1, col=1)
for trace in fig_barras.data: fig_dashboard.add_trace(trace, row=1, col=2)
for trace in fig_linha.data: fig_dashboard.add_trace(trace, row=2, col=1)

fig_dashboard.update_layout(height=750, showlegend=True, template="plotly_white")
fig_dashboard.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.05, xanchor="center", x=0.5))

# Exibe o Dashboard
st.plotly_chart(fig_dashboard, use_container_width=True)

# Tabela Oculta
with st.expander("📋 Clique para ver a Tabela de Dados Brutos"):
    st.dataframe(df, use_container_width=True)
