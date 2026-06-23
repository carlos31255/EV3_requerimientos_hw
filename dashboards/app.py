import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector
import os

st.set_page_config(page_title="Hardware Intelligence", layout="wide", page_icon="💻")

# Conexión a DB usando st.cache_resource para no reconectar en cada refresh
@st.cache_resource
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=3306,
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            database=os.environ.get('DB_NAME', 'tienda_hardware_intelligence')
        )
    except Exception as e:
        st.error(f"Error de conexión a MySQL: {e}")
        return None

# Cargar datos básicos de DB
@st.cache_data
def get_data():
    conn = get_db_connection()
    if not conn:
        return None, None, None, None
        
    df_comp = pd.read_sql("SELECT * FROM component", conn)
    df_prices = pd.read_sql("SELECT * FROM market_prices_external", conn)
    df_steam = pd.read_sql("SELECT * FROM steam_hardware_survey", conn)
    df_tiers = pd.read_sql("SELECT * FROM component_tiers", conn)
    return df_comp, df_prices, df_steam, df_tiers

df_comp, df_prices, df_steam, df_tiers = get_data()

# ==========================================
# HEADER Y ESTILO
# ==========================================
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>💻 Dashboard de Hardware Intelligence</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Plataforma interactiva para el análisis de precios, demanda y popularidad global (Datos de Steam & eBay).</p>", unsafe_allow_html=True)
st.divider()

if df_comp is not None and not df_comp.empty:
    df_prices_full = df_prices.merge(df_comp[['id', 'name', 'categoria']], left_on='component_id', right_on='id')
    df_steam_full = df_steam.merge(df_comp[['id', 'name', 'categoria']], left_on='component_id', right_on='id')
    
    # ==========================================
    # SECCIÓN 1: MÉTRICAS CLAVE (KPIs)
    # ==========================================
    st.subheader("🎯 Resumen del Mercado")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.metric(label="📦 Total Componentes", value=len(df_comp))
        
    with kpi2:
        gpu_mas_cara = df_prices_full[df_prices_full['categoria'] == 'GPU'].sort_values('price_clp', ascending=False).iloc[0]
        st.metric(label="💸 GPU Más Cara", value=gpu_mas_cara['name'], delta=f"- ${gpu_mas_cara['price_clp']:,.0f} CLP", delta_color="inverse")
        
    with kpi3:
        cpu_popular = df_steam_full[df_steam_full['categoria'] == 'CPU'].sort_values('global_share_percentage', ascending=False).iloc[0]
        st.metric(label="🔥 CPU Más Popular (Steam)", value=cpu_popular['name'], delta=f"{cpu_popular['global_share_percentage']}% de uso")

    with kpi4:
        gpu_popular = df_steam_full[df_steam_full['categoria'] == 'GPU'].sort_values('global_share_percentage', ascending=False).iloc[0]
        st.metric(label="🎮 GPU Más Popular (Steam)", value=gpu_popular['name'], delta=f"{gpu_popular['global_share_percentage']}% de uso")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # SECCIÓN 2: GRÁFICOS PRINCIPALES
    # ==========================================
    col_izq, col_der = st.columns([1.5, 1])
    
    with col_izq:
        st.markdown("### 🏷️ Análisis de Precios de Referencia (CLP)")
        # Gráfico más elegante con fondo transparente
        df_precios_sorted = df_prices_full.sort_values('price_clp', ascending=True)
        fig_precios = px.bar(
            df_precios_sorted,
            x='price_clp', y='name',
            color='categoria',
            orientation='h',
            text=df_precios_sorted['price_clp'].apply(lambda x: f'${x:,.0f}'),
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_precios.update_traces(textposition='outside', textfont=dict(size=11))
        fig_precios.update_layout(
            height=450,
            margin=dict(l=0, r=120, t=30, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Precio (CLP)",
            yaxis_title="",
            xaxis=dict(showticklabels=False)
        )
        st.plotly_chart(fig_precios, use_container_width=True)

    with col_der:
        st.markdown("### 📊 Distribución de Inventario por Gama")
        df_comp_tiers = df_comp.merge(df_tiers, left_on='component_tiers_id', right_on='id')
        tier_dist = df_comp_tiers.groupby(['categoria', 'tier_name']).size().reset_index(name='cantidad')

        fig_tiers = px.bar(
            tier_dist,
            x='categoria', y='cantidad',
            color='tier_name',
            barmode='group',
            text='cantidad',
            color_discrete_map={'Gama Baja': '#3498db', 'Gama Media': '#2ecc71', 'Gama Alta': '#e74c3c'}
        )
        fig_tiers.update_traces(textposition='outside')
        fig_tiers.update_layout(
            height=450,
            margin=dict(l=0, r=0, t=30, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Categoría",
            yaxis_title="Cantidad",
            legend_title="Gama"
        )
        st.plotly_chart(fig_tiers, use_container_width=True)

    # ==========================================
    # SECCIÓN 3: STEAM HARDWARE SURVEY
    # ==========================================
    st.divider()
    st.markdown("### 🔢 Variedad de Componentes por Categoría")
    variedad = df_steam_full.groupby('categoria')['name'].nunique().reset_index()
    variedad.columns = ['categoria', 'modelos_unicos']

    fig_variedad = px.bar(
        variedad.sort_values('modelos_unicos', ascending=False),
        x='categoria', y='modelos_unicos',
        text='modelos_unicos',
        color='categoria',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_variedad.update_traces(textposition='outside')
    fig_variedad.update_layout(
        height=350,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Categoría",
        yaxis_title="Modelos únicos",
        showlegend=False
    )
    st.plotly_chart(fig_variedad, use_container_width=True)

    # Detalle de componentes por categoría
    with st.expander("📋 Ver detalle de componentes por categoría"):
        for cat in variedad.sort_values('modelos_unicos', ascending=False)['categoria']:
            componentes = df_steam_full[df_steam_full['categoria'] == cat][['name', 'global_share_percentage']].sort_values('global_share_percentage', ascending=False)
            componentes.columns = ['Componente', '% usuarios Steam']
            st.markdown(f"**{cat}**")
            st.dataframe(componentes, use_container_width=True, hide_index=True)
else:
    st.error("⚠️ No se encontraron datos en la base de datos o MySQL no está corriendo.")