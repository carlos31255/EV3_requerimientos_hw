import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
import os

st.set_page_config(page_title="PC Upgrade Advisor", layout="wide", page_icon="🖥️")

# ==========================================
# ESTILOS
# ==========================================
st.markdown("""
<style>
    .audience-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .badge-ejecutiva { background-color: #1a1a2e; color: #e94560; }
    .badge-tecnica   { background-color: #16213e; color: #0f3460; color: #4fc3f7; }
    .badge-operativa { background-color: #1b2838; color: #57cbde; }
    .kpi-card { padding: 1rem; border-radius: 8px; background: #1e1e2e; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONEXIÓN Y DATOS
# ==========================================
@st.cache_resource
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=int(os.environ.get('DB_PORT', 3307)),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            database=os.environ.get('DB_NAME', 'tienda_hardware_intelligence')
        )
    except Exception as e:
        st.error(f"Error de conexión a MySQL: {e}")
        return None

@st.cache_data
def get_data():
    conn = get_db_connection()
    if not conn:
        return {}
    return {
        'componentes': pd.read_sql("SELECT * FROM component", conn),
        'precios':     pd.read_sql("SELECT * FROM market_prices_external", conn),
        'steam':       pd.read_sql("SELECT * FROM steam_hardware_survey", conn),
        'tiers':       pd.read_sql("SELECT * FROM component_tiers", conn),
        'juegos':      pd.read_sql("SELECT * FROM games", conn),
        'requisitos':  pd.read_sql("SELECT * FROM game_requeriments", conn),
        'builds':      pd.read_sql("SELECT bt.template_name, bt.description, c.name as componente, c.categoria FROM build_templates bt JOIN build_components bc ON bt.id = bc.build_templates_id JOIN component c ON bc.component_id = c.id", conn),
        'inventario':  pd.read_sql("SELECT * FROM store_inventory", conn),
    }

data = get_data()

if not data:
    st.error("⚠️ No se pudo conectar a la base de datos.")
    st.stop()

# ==========================================
# PREPARAR DATAFRAMES CRUZADOS
# ==========================================
df_comp     = data['componentes']
df_precios  = data['precios']
df_steam    = data['steam']
df_tiers    = data['tiers']
df_juegos   = data['juegos']
df_req      = data['requisitos']
df_builds   = data['builds']
df_inv      = data['inventario']

df_precios_full = df_precios.merge(df_comp[['id','name','categoria','component_tiers_id']], left_on='component_id', right_on='id')
df_precios_full = df_precios_full.merge(df_tiers[['id','tier_name']], left_on='component_tiers_id', right_on='id', how='left')
df_steam_full   = df_steam.merge(df_comp[['id','name','categoria']], left_on='component_id', right_on='id')

# Cruce juegos → requisitos → componente → precio
df_req_full = (df_req
    .merge(df_juegos[['id','titulo']], left_on='games_id', right_on='id')
    .merge(df_comp[['id','name','categoria']], left_on='component_id', right_on='id')
    .merge(df_precios[['component_id','price_clp']], on='component_id', how='left')
)

# Inventario con precios
df_inv_full = (df_inv
    .merge(df_comp[['id','name','categoria']], left_on='component_id', right_on='id')
    .merge(df_precios[['component_id','price_clp']], on='component_id', how='left')
)
df_inv_full['diferencia_clp'] = df_inv_full['store_price_clp'] - df_inv_full['price_clp']
df_inv_full['competitivo'] = df_inv_full['diferencia_clp'].apply(
    lambda x: '✅ Competitivo' if x <= 0 else ('⚠️ Precio alto' if x < 50000 else '🚨 Muy caro')
)

# ==========================================
# HEADER
# ==========================================
st.markdown("<h1 style='text-align:center;'>🖥️ PC Upgrade Advisor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>Sistema inteligente de recomendación de componentes · Steam HW Survey + eBay API + Kaggle</p>", unsafe_allow_html=True)
st.divider()

# ==========================================
# TABS POR AUDIENCIA
# ==========================================
tab_exec, tab_tec, tab_op = st.tabs([
    "📊 Vista Ejecutiva",
    "🔧 Vista Técnica",
    "🎮 Vista Operativa — Recomendador"
])

# ==========================================
# TAB 1: VISTA EJECUTIVA
# ==========================================
with tab_exec:
    st.markdown("<span class='audience-badge badge-ejecutiva'>👔 Audiencia Ejecutiva</span>", unsafe_allow_html=True)
    st.markdown("### Resumen del mercado de componentes PC")

    # KPIs
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Componentes catalogados", len(df_comp))
    with k2:
        gpu_pop = df_steam_full[df_steam_full['categoria']=='GPU'].sort_values('global_share_percentage', ascending=False).iloc[0]
        st.metric("GPU más popular (Steam)", gpu_pop['name'], f"{gpu_pop['global_share_percentage']}%")
    with k3:
        ram_pop = df_steam_full[df_steam_full['categoria']=='RAM'].sort_values('global_share_percentage', ascending=False).iloc[0]
        st.metric("RAM estándar (Steam)", ram_pop['name'], f"{ram_pop['global_share_percentage']}%")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💰 Precio de mercado por componente (CLP)")
        
        # Filtro por categoría para no sobrecargar el gráfico
        categorias_disp = ['Todas'] + list(df_precios_full['categoria'].unique())
        cat_filtro = st.selectbox("Filtrar por categoría:", categorias_disp)
        
        df_sorted = df_precios_full.sort_values('price_clp', ascending=True)
        if cat_filtro != 'Todas':
            df_sorted = df_sorted[df_sorted['categoria'] == cat_filtro]
            
        fig = px.bar(
            df_sorted, x='price_clp', y='name', orientation='h',
            color='tier_name', text=df_sorted['price_clp'].apply(lambda x: f'${x:,.0f}'),
            color_discrete_map={'Gama Baja':'#3498db','Gama Media':'#2ecc71','Gama Alta':'#e74c3c'},
            labels={'price_clp':'Precio CLP','name':'','tier_name':'Gama'}
        )
        fig.update_traces(textposition='outside')
        
        # Ajustar altura dinámicamente según la cantidad de items
        altura_dinamica = max(300, len(df_sorted) * 35)
        
        fig.update_layout(height=altura_dinamica, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          margin=dict(r=120,l=0,t=10,b=0), xaxis=dict(showticklabels=False))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 📈 Uso en Steam (% jugadores globales)")
        
        # Filtro por categoría para Steam
        categorias_steam = list(df_steam_full['categoria'].unique())
        cat_steam_filtro = st.selectbox("Filtrar Steam por categoría:", categorias_steam)

        df_steam_filtered = df_steam_full[df_steam_full['categoria']==cat_steam_filtro].sort_values('global_share_percentage', ascending=True)
        
        fig2 = px.bar(
            df_steam_filtered, x='global_share_percentage', y='name', orientation='h',
            color='global_share_percentage', color_continuous_scale='Tealgrn',
            text=df_steam_filtered['global_share_percentage'].apply(lambda x: f'{x:.2f}%'),
            labels={'global_share_percentage':'% usuarios','name':''}
        )
        fig2.update_traces(textposition='outside')
        
        # Ajustar altura dinámicamente
        altura_dinamica_steam = max(300, len(df_steam_filtered) * 35)
        
        fig2.update_layout(height=altura_dinamica_steam, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           margin=dict(r=80,l=0,t=10,b=0), coloraxis_showscale=False,
                           xaxis=dict(showticklabels=False))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    st.markdown("#### 📦 Catálogo de componentes: 20 modelos distribuidos en 3 gamas y 6 categorías")
    df_comp_tiers = df_comp.merge(df_tiers, left_on='component_tiers_id', right_on='id')
    tier_dist = df_comp_tiers.groupby(['categoria','tier_name']).size().reset_index(name='cantidad')
    # Asegurar orden correcto visual
    orden_gama = ['Gama Baja', 'Gama Media', 'Gama Alta']
    tier_dist['tier_name'] = pd.Categorical(tier_dist['tier_name'], categories=orden_gama, ordered=True)
    tier_dist = tier_dist.sort_values(['categoria', 'tier_name'])

    fig3 = px.bar(
        tier_dist, x='categoria', y='cantidad', color='tier_name', barmode='group', text='cantidad',
        color_discrete_map={'Gama Baja':'#3498db','Gama Media':'#2ecc71','Gama Alta':'#e74c3c'},
        labels={'categoria':'Categoría','cantidad':'Componentes','tier_name':'Gama'}
    )
    fig3.update_traces(textposition='outside')
    fig3.update_layout(yaxis=dict(range=[0, tier_dist['cantidad'].max() + 1]))
    fig3.update_layout(height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                       margin=dict(t=10,b=0))
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()



# ==========================================
# TAB 2: VISTA TÉCNICA
# ==========================================
with tab_tec:
    st.markdown("<span class='audience-badge badge-tecnica'>🔧 Audiencia Técnica</span>", unsafe_allow_html=True)
    st.markdown("### 📊 Análisis de Requisitos de Juegos")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📈 RAM Recomendada por juego (GB)")
        df_ram_db = df_req_full[(df_req_full['categoria'] == 'RAM') & (df_req_full['requirement_type'] == 'Recommended')].copy()
        df_ram_db['ram_gb'] = df_ram_db['name'].str.extract(r'(\d+)GB').astype(float)
        df_ram_db = df_ram_db.sort_values('ram_gb')
        
        fig_ram = px.bar(
            df_ram_db, x='ram_gb', y='titulo', orientation='h',
            color='ram_gb', color_continuous_scale='Purp',
            labels={'ram_gb':'GB de RAM', 'titulo':''},
            text=df_ram_db['ram_gb'].apply(lambda x: f'{int(x)} GB')
        )
        fig_ram.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig_ram, use_container_width=True)

    with col2:
        st.markdown("#### 🔍 GPUs más exigidas (Recomendados)")
        df_gpu_db = df_req_full[(df_req_full['categoria'] == 'GPU') & (df_req_full['requirement_type'] == 'Recommended')]
        gpu_counts = df_gpu_db['name'].value_counts().reset_index()
        gpu_counts.columns = ['GPU', 'Frecuencia']
        
        fig_gpus = px.bar(
            gpu_counts, x='Frecuencia', y='GPU', orientation='h',
            color='Frecuencia', color_continuous_scale='OrRd',
            labels={'Frecuencia':'Nº de juegos', 'GPU':''}
        )
        fig_gpus.update_layout(height=200, margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig_gpus, use_container_width=True)

        st.markdown("#### ⚙️ CPUs más exigidas (Recomendados)")
        df_cpu_db = df_req_full[(df_req_full['categoria'] == 'CPU') & (df_req_full['requirement_type'] == 'Recommended')]
        cpu_counts = df_cpu_db['name'].value_counts().reset_index()
        cpu_counts.columns = ['CPU', 'Frecuencia']
        
        fig_cpus = px.bar(
            cpu_counts, x='Frecuencia', y='CPU', orientation='h',
            color='Frecuencia', color_continuous_scale='Blues',
            labels={'Frecuencia':'Nº de juegos', 'CPU':''}
        )
        fig_cpus.update_layout(height=200, margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig_cpus, use_container_width=True)

    st.divider()
    st.markdown("#### 📋 Tabla completa de requisitos")
    df_tabla_full = df_req_full[['titulo','requirement_type','categoria','name']].copy()
    st.dataframe(df_tabla_full, use_container_width=True, hide_index=True)

# ==========================================
# TAB 3: VISTA OPERATIVA — RECOMENDADOR
# ==========================================
with tab_op:
    st.markdown("<span class='audience-badge badge-operativa'>🎮 Audiencia Operativa</span>", unsafe_allow_html=True)
    st.markdown("### ¿Qué necesito para jugar?")

    col_izq, col_der = st.columns([1, 1.5])

    with col_izq:
        st.markdown("#### 🕹️ Selecciona tu perfil")
        juego_op = st.selectbox("Juego objetivo", df_juegos['titulo'].tolist(), key='op_juego')
        req_type = st.radio("Nivel de requisito", ['Minimum', 'Recommended'], horizontal=True)

        target_str_op = "1080p 60fps (Recomendado)" if req_type == 'Recommended' else "720p 30fps (Mínimo)"
        st.info(f"🎯 Rendimiento esperado: {target_str_op}")

        df_sel = df_req_full[(df_req_full['titulo']==juego_op) & (df_req_full['requirement_type']==req_type)]
        costo_total = df_sel['price_clp'].sum()

        st.markdown("---")
        st.markdown(f"**Componentes necesarios:**")
        for _, r in df_sel.iterrows():
            precio = f"${r['price_clp']:,.0f} CLP" if pd.notna(r.get('price_clp')) else "Sin precio"
            st.markdown(f"- **{r['categoria']}**: {r['name']} · {precio}")

        st.markdown("---")
        if costo_total > 0:
            st.info(f"💰 **Costo total estimado:** ${costo_total:,.0f} CLP")

    with col_der:
        st.markdown("#### 🏗️ Builds populares de referencia")

        # Usar BD para mostrar builds
        for build_name in df_builds['template_name'].unique():
            df_b = df_builds[df_builds['template_name']==build_name]
            with st.expander(f"**{build_name}**"):
                for _, r in df_b.iterrows():
                    st.markdown(f"- **{r['categoria']}**: {r['componente']}")




