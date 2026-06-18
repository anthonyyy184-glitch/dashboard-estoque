import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(page_title="Gestão de Estoque", layout="wide")

# Estilização CSS para criar blocos modernos e limpos (Cards)
st.markdown("""
    <style>
    .kpi-box {
        background-color: #1F2937;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .kpi-title {
        color: #9CA3AF;
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .kpi-value {
        color: #FFFFFF;
        font-size: 28px;
        font-weight: bold;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Novo Título Corporativo e Elegante
st.markdown("<h2 style='color: #FFFFFF; font-family: Arial, sans-serif; font-weight: 700; margin-bottom: 5px;'>📈 Painel de Monitoramento de Logística</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #9CA3AF; margin-bottom: 25px;'>Acompanhamento de Movimentações, Saldos e Distribuição de Culturas</p>", unsafe_allow_html=True)

# --- REPOSITÓRIO DE DADOS ---
st.sidebar.markdown("<h2 style='color: #FFFFFF;'>🔄 Gestão de Dados</h2>", unsafe_allow_html=True)
arquivo_subido = st.sidebar.file_uploader("📥 Upload de Nova Base (.csv ou .xlsx)", type=["csv", "xlsx"])

if arquivo_subido is not None:
    try:
        if arquivo_subido.name.endswith('.csv'):
            df = pd.read_csv(arquivo_subido)
        else:
            df = pd.read_excel(arquivo_subido)
        st.sidebar.success("✅ Arquivo carregado com sucesso!")
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao ler o arquivo: {e}")
        df = pd.read_csv("Base_Tabular_SQL.csv")
else:
    df = pd.read_csv("Base_Tabular_SQL.csv")

# --- PADRONIZAÇÃO AUTOMÁTICA DE COLUNAS (Evita o erro de ficar parado) ---
# Remove espaços antes/depois e deixa tudo em minúsculo para comparar fácil
df.columns = df.columns.str.strip()
mapeamento_colunas = {}

for col in df.columns:
    col_lower = col.lower()
    if 'ent' in col_lower: mapeamento_colunas[col] = 'Entrada'
    elif 'sa' in col_lower or 'sai' in col_lower: mapeamento_colunas[col] = 'Saída'
    elif 'dat' in col_lower: mapeamento_colunas[col] = 'Data'
    elif 'prod' in col_lower: mapeamento_colunas[col] = 'Produtor'
    elif 'cat' in col_lower or 'cult' in col_lower: mapeamento_colunas[col] = 'Categoria'

df = df.rename(columns=mapeamento_colunas)

# Garante que as colunas essenciais existam (se não existirem, cria com zero para não quebrar)
for col_essencial in ['Entrada', 'Saída', 'Produtor', 'Categoria']:
    if col_essencial not in df.columns:
        df[col_essencial] = 0 if col_essencial in ['Entrada', 'Saída'] else 'Não Informado'

# Tratamento dos formatos
df["Entrada"] = pd.to_numeric(df["Entrada"], errors='coerce').fillna(0)
df["Saída"] = pd.to_numeric(df["Saída"], errors='coerce').fillna(0)

if 'Data' in df.columns:
    df["Data_Tratada"] = pd.to_datetime(df["Data"], errors='coerce')
    # Se falhar o formato padrão, tenta tratar os textos
    if df["Data_Tratada"].isna().all():
        df["Data_Tratada"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors='coerce')
    df["Ano_Mes"] = df["Data_Tratada"].dt.to_period("M").astype(str)
else:
    df["Ano_Mes"] = "Sem Data"

# Filtro integrado na barra lateral
st.sidebar.markdown("---")
categorias = ["Todas as Categorias"] + list(df["Categoria"].dropna().unique())
cat_sel = st.sidebar.selectbox("Filtrar Cultura:", categorias)
if cat_sel != "Todas as Categorias":
    df = df[df["Categoria"] == cat_sel]

# Cálculos de Performance
total_entradas = df["Entrada"].sum()
total_saidas = df["Saída"].sum()
saldo_estoque = total_entradas - total_saidas

# --- EXIBIÇÃO DOS CARDS PREMIUM ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class='kpi-box'><div class='kpi-title'>Volume de Entradas</div><div class='kpi-value'>{total_entradas:,.0f} Kg</div></div>""".replace(",", "."), unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class='kpi-box' style='border-left-color: #EF4444;'><div class='kpi-title'>Volume de Saídas</div><div class='kpi-value'>{total_saidas:,.0f} Kg</div></div>""".replace(",", "."), unsafe_allow_html=True)
with col3:
    cor_saldo = "#10B981" if saldo_estoque >= 0 else "#EF4444"
    st.markdown(f"""<div class='kpi-box' style='border-left-color: {cor_saldo};'><div class='kpi-title'>Saldo em Estoque</div><div class='kpi-value'>{saldo_estoque:,.0f} Kg</div></div>""".replace(",", "."), unsafe_allow_html=True)

# Abas de Navegação Módula
aba_painel, aba_dados = st.tabs(["📊 DASHBOARD ANALÍTICO", "📋 BASE DE DADOS TABULAR"])

with aba_painel:
    # Gráfico de Rosca
    df_contagem = df["Categoria"].value_counts().reset_index()
    df_contagem.columns = ["Categoria", "Qtd"]
    fig_rosca = px.pie(df_contagem, names="Categoria", values="Qtd", hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_rosca.update_traces(textposition='inside', textinfo='percent')
    fig_rosca.update_layout(title="Divisão por Categoria de Operação", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    # Gráfico de Barras
    top_produtores = df.groupby("Produtor")["Entrada"].sum().reset_index()
    top_produtores = top_produtores[~top_produtores["Produtor"].astype(str).str.lower().str.contains("estoque|fato|não informado", na=True)]
    top_produtores = top_produtores.sort_values(by="Entrada", ascending=False).head(5)
    
    if not top_produtores.empty:
        fig_barras = px.bar(top_produtores, x="Entrada", y="Produtor", orientation='h', color_discrete_sequence=["#3B82F6"])
        fig_barras.update_layout(yaxis={'categoryorder':'total ascending'}, title="Top 5 Fornecedores Líderes (Kg)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    else:
        fig_barras = go.Figure()
        fig_barras.update_layout(title="Sem dados de produtores para exibir", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    # Gráfico de Linhas
    df_temporal = df[~df["Ano_Mes"].isin(["NaT", "Sem Data"])].groupby("Ano_Mes")[["Entrada", "Saída"]].sum().reset_index().sort_values("Ano_Mes")
    fig_linha = go.Figure()
    if not df_temporal.empty:
        fig_linha.add_trace(go.Scatter(x=df_temporal["Ano_Mes"], y=df_temporal["Entrada"], mode='lines+markers', name='Entradas', line=dict(color='#10B981', width=3)))
        fig_linha.add_trace(go.Scatter(x=df_temporal["Ano_Mes"], y=df_temporal["Saída"], mode='lines+markers', name='Saídas', line=dict(color='#EF4444', width=3)))
    fig_linha.update_layout(title="Fluxo de Carga Mensal (Evolução)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))

    # Layout em Linhas Limpas
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(fig_rosca, use_container_width=True)
    with c2: st.plotly_chart(fig_barras, use_container_width=True)
    st.markdown("---")
    st.plotly_chart(fig_linha, use_container_width=True)

with aba_dados:
    st.dataframe(df, use_container_width=True)
