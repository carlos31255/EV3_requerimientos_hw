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
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='tienda_hardware_intelligence'
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

st.title("💻 Dashboard de Inteligencia de Hardware")
st.markdown("Visualización interactiva de datos del mercado y popularidad de componentes en Steam.")

if df_comp is not None and not df_comp.empty:
    # Preparar df_prices con nombres de componentes
    df_prices_full = df_prices.merge(df_comp[['id', 'name', 'categoria']], left_on='component_id', right_on='id')
    
    # 1. KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Componentes Registrados", len(df_comp))
    
    gpu_mas_cara = df_prices_full[df_prices_full['categoria'] == 'GPU'].sort_values('price_clp', ascending=False).iloc[0]
    col2.metric("GPU Más Cara", gpu_mas_cara['name'], f"${gpu_mas_cara['price_clp']:,.0f} CLP")
    
    df_steam_full = df_steam.merge(df_comp[['id', 'name', 'categoria']], left_on='component_id', right_on='id')
    comp_mas_popular = df_steam_full.sort_values('global_share_percentage', ascending=False).iloc[0]
    col3.metric("Más Popular (Steam)", comp_mas_popular['name'], f"{comp_mas_popular['global_share_percentage']}% uso global")
    
    st.markdown("---")
    
    # 2. Gráficos
    st.subheader("Análisis de Precios de Mercado (API eBay)")
    fig_precios = px.bar(
        df_prices_full.sort_values('price_clp', ascending=False),
        x='name', y='price_clp',
        color='categoria',
        title='Precios de Referencia (CLP)',
        text=df_prices_full.sort_values('price_clp', ascending=False)['price_clp'].apply(lambda x: f'${x:,.0f}'),
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_precios.update_traces(textposition='outside')
    fig_precios.update_layout(height=450)
    st.plotly_chart(fig_precios, use_container_width=True)
    
    st.markdown("---")
    
    colA, colB = st.columns(2)
    
    with colA:
        st.subheader("Distribución de Catálogo por Gama")
        df_comp_tiers = df_comp.merge(df_tiers, left_on='component_tiers_id', right_on='id')
        tier_dist = df_comp_tiers.groupby(['categoria', 'tier_name']).size().reset_index(name='cantidad')
        fig_tiers = px.bar(
            tier_dist,
            x='categoria', y='cantidad',
            color='tier_name',
            barmode='group',
            title='Componentes por Categoría y Gama',
            color_discrete_map={'Gama Baja': '#3498db', 'Gama Media': '#2ecc71', 'Gama Alta': '#e74c3c'}
        )
        st.plotly_chart(fig_tiers, use_container_width=True)
        
    with colB:
        st.subheader("Hardware Popular en Steam")
        fig_steam = px.bar(
            df_steam_full.sort_values('global_share_percentage', ascending=True),
            x='global_share_percentage', y='name',
            orientation='h',
            color='categoria',
            title='Porcentaje de Usuarios Globales (%)',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_steam, use_container_width=True)

else:
    st.warning("No se encontraron datos en la base de datos o MySQL no está corriendo.")
