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
            port=3306,
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

def get_csv_data():
    steam_csv = pd.read_csv("data/steam_sample_15.csv") if os.path.exists("data/steam_sample_15.csv") else None
    builds_csv = pd.read_csv("data/builds_populares.csv") if os.path.exists("data/builds_populares.csv") else None
    return steam_csv, builds_csv

data = get_data()
steam_csv, builds_csv = get_csv_data()

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
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Componentes catalogados", len(df_comp))
    with k2:
        total_inv = df_inv_full['store_price_clp'].sum()
        st.metric("Valor total catálogo", f"${total_inv:,.0f} CLP")
    with k3:
        gpu_pop = df_steam_full[df_steam_full['categoria']=='GPU'].sort_values('global_share_percentage', ascending=False).iloc[0]
        st.metric("GPU más popular (Steam)", gpu_pop['name'], f"{gpu_pop['global_share_percentage']}%")
    with k4:
        ram_pop = df_steam_full[df_steam_full['categoria']=='RAM'].sort_values('global_share_percentage', ascending=False).iloc[0]
        st.metric("Estándar de RAM global", ram_pop['name'], f"{ram_pop['global_share_percentage']}% de jugadores")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💰 Precio de mercado por componente (CLP)")
        df_sorted = df_precios_full.sort_values('price_clp', ascending=True)
        fig = px.bar(
            df_sorted, x='price_clp', y='name', orientation='h',
            color='tier_name', text=df_sorted['price_clp'].apply(lambda x: f'${x:,.0f}'),
            color_discrete_map={'Gama Baja':'#3498db','Gama Media':'#2ecc71','Gama Alta':'#e74c3c'},
            labels={'price_clp':'Precio CLP','name':'','tier_name':'Gama'}
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(height=420, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          margin=dict(r=120,l=0,t=10,b=0), xaxis=dict(showticklabels=False))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🎮 GPUs más usadas en Steam (% jugadores globales)")
        df_gpu_steam = df_steam_full[df_steam_full['categoria']=='GPU'].sort_values('global_share_percentage', ascending=True)
        fig2 = px.bar(
            df_gpu_steam, x='global_share_percentage', y='name', orientation='h',
            color='global_share_percentage', color_continuous_scale='Tealgrn',
            text=df_gpu_steam['global_share_percentage'].apply(lambda x: f'{x:.2f}%'),
            labels={'global_share_percentage':'% usuarios','name':''}
        )
        fig2.update_traces(textposition='outside')
        fig2.update_layout(height=420, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           margin=dict(r=80,l=0,t=10,b=0), coloraxis_showscale=False,
                           xaxis=dict(showticklabels=False))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 📦 Distribución del catálogo por gama y categoría")
    df_comp_tiers = df_comp.merge(df_tiers, left_on='component_tiers_id', right_on='id')
    tier_dist = df_comp_tiers.groupby(['categoria','tier_name']).size().reset_index(name='cantidad')
    fig3 = px.bar(
        tier_dist, x='categoria', y='cantidad', color='tier_name', barmode='group', text='cantidad',
        color_discrete_map={'Gama Baja':'#3498db','Gama Media':'#2ecc71','Gama Alta':'#e74c3c'},
        labels={'categoria':'Categoría','cantidad':'Componentes','tier_name':'Gama'}
    )
    fig3.update_traces(textposition='outside')
    fig3.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                       margin=dict(t=10,b=0))
    st.plotly_chart(fig3, use_container_width=True)

# ==========================================
# TAB 2: VISTA TÉCNICA
# ==========================================
with tab_tec:
    st.markdown("<span class='audience-badge badge-tecnica'>🔧 Audiencia Técnica</span>", unsafe_allow_html=True)
    st.markdown("### Análisis técnico de componentes y requisitos de juegos")

    # Cargar games_sample_15.csv
    games_path = "data/kaggle/games_sample_15.csv"
    if os.path.exists(games_path):
        df_games15 = pd.read_csv(games_path)
    else:
        df_games15 = None

    if df_games15 is not None:

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🎮 Requisitos por juego")
            juego_sel = st.selectbox("Selecciona un juego", df_games15['game_name'].tolist())
            row_juego = df_games15[df_games15['game_name'] == juego_sel].iloc[0]
            st.markdown(f"🖥️ **CPU:** {row_juego['cpu']}")
            st.markdown(f"🎮 **GPU:** {row_juego['gpu']}")
            st.markdown(f"💾 **RAM:** {row_juego['ram']}")
            st.markdown(f"💿 **Storage:** {row_juego['storage']}")
            st.markdown(f"🪟 **OS:** {row_juego['os']}")
            st.info(f"🎯 Target: {row_juego['target_performance']}")

        with col2:
            st.markdown("#### 💾 RAM requerida por juego (GB)")
            df_ram_req = df_games15.copy()
            df_ram_req['ram_gb'] = df_ram_req['ram'].str.extract(r'(\d+)').astype(float)
            df_ram_req = df_ram_req.sort_values('ram_gb', ascending=True)
            fig_ram_req = px.bar(
                df_ram_req, x='ram_gb', y='game_name', orientation='h',
                color='ram_gb', color_continuous_scale='Blues',
                text=df_ram_req['ram_gb'].apply(lambda x: f'{int(x)} GB'),
                labels={'ram_gb':'RAM (GB)', 'game_name':''}
            )
            fig_ram_req.update_traces(textposition='outside')
            fig_ram_req.update_layout(
                height=450, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(r=80,l=0,t=10,b=0), coloraxis_showscale=False,
                xaxis=dict(showticklabels=False)
            )
            st.plotly_chart(fig_ram_req, use_container_width=True)

        st.divider()

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("#### 🔍 GPUs más exigidas por los 15 juegos")
            # Extraer GPUs mencionadas (primer modelo antes de 'o')
            df_games15['gpu_principal'] = df_games15['gpu'].str.split(' o ').str[0].str.strip()
            gpu_freq = df_games15['gpu_principal'].value_counts().reset_index()
            gpu_freq.columns = ['gpu', 'juegos']
            fig_gpu_freq = px.bar(
                gpu_freq, x='juegos', y='gpu', orientation='h',
                text='juegos', color='juegos', color_continuous_scale='Reds',
                labels={'juegos':'Nº de juegos', 'gpu':'GPU'}
            )
            fig_gpu_freq.update_traces(textposition='outside')
            fig_gpu_freq.update_layout(
                height=380, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(r=60,l=0,t=10,b=0), coloraxis_showscale=False,
                xaxis=dict(showticklabels=False)
            )
            st.plotly_chart(fig_gpu_freq, use_container_width=True)

        with col4:
            st.markdown("#### 🎯 Perfil de rendimiento objetivo por juego")
            perf_count = df_games15['target_performance'].value_counts().reset_index()
            perf_count.columns = ['perfil', 'cantidad']
            fig_perf = px.pie(
                perf_count, names='perfil', values='cantidad',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4
            )
            fig_perf.update_traces(textposition='inside', textinfo='percent+label')
            fig_perf.update_layout(
                height=380, margin=dict(t=10,b=0),
                showlegend=False
            )
            st.plotly_chart(fig_perf, use_container_width=True)

        st.divider()
        st.markdown("#### 📋 Tabla completa de requisitos")
        df_tabla_games = df_games15[['game_name','cpu','gpu','ram','storage','target_performance']].copy()
        df_tabla_games.columns = ['Juego','CPU','GPU','RAM','Storage','Target']
        st.dataframe(df_tabla_games, use_container_width=True, hide_index=True)

    else:
        st.warning("⚠️ No se encontró `data/kaggle/games_sample_15.csv`. Asegúrate de correr `extraer_muestra.py` primero.")
        # Fallback a DB
        st.markdown("#### 📋 Componentes desde DB")
        df_tabla = df_precios_full[['name','categoria','tier_name','price_clp']].copy()
        df_tabla.columns = ['Componente','Categoría','Gama','Precio CLP']
        df_tabla['Precio CLP'] = df_tabla['Precio CLP'].apply(lambda x: f'${x:,.0f}')
        st.dataframe(df_tabla, use_container_width=True, hide_index=True)

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
        presupuesto = st.number_input("Presupuesto máximo (CLP)", min_value=0, value=500000, step=50000)

        df_sel = df_req_full[(df_req_full['titulo']==juego_op) & (df_req_full['requirement_type']==req_type)]
        costo_total = df_sel['price_clp'].sum()

        st.markdown("---")
        st.markdown(f"**Componentes necesarios:**")
        for _, r in df_sel.iterrows():
            precio = f"${r['price_clp']:,.0f} CLP" if pd.notna(r.get('price_clp')) else "Sin precio"
            st.markdown(f"- **{r['categoria']}**: {r['name']} · {precio}")

        st.markdown("---")
        if costo_total > 0:
            if costo_total <= presupuesto:
                st.success(f"✅ Costo estimado: ${costo_total:,.0f} CLP · Dentro de tu presupuesto")
            else:
                faltante = costo_total - presupuesto
                st.error(f"❌ Costo estimado: ${costo_total:,.0f} CLP · Te faltan ${faltante:,.0f} CLP")

    with col_der:
        st.markdown("#### 🏗️ Builds populares de referencia")

        # Usar CSV si está disponible, sino DB
        if builds_csv is not None:
            df_builds_show = builds_csv
            for _, build in df_builds_show.iterrows():
                with st.expander(f"**{build['build_name']}** · {build['target_profile']}"):
                    cols = st.columns(2)
                    with cols[0]:
                        st.markdown(f"🖥️ **CPU:** {build['cpu']}")
                        st.markdown(f"🎮 **GPU:** {build['gpu']}")
                    with cols[1]:
                        st.markdown(f"💾 **RAM:** {build['ram']}")
                        st.markdown(f"💿 **Storage:** {build['storage']}")
        else:
            for build_name in df_builds['template_name'].unique():
                df_b = df_builds[df_builds['template_name']==build_name]
                with st.expander(f"**{build_name}**"):
                    for _, r in df_b.iterrows():
                        st.markdown(f"- **{r['categoria']}**: {r['componente']}")

        st.divider()
        st.markdown("#### 📊 Estándar actual de RAM en jugadores Steam")
        
        # Leer SIEMPRE de la Base de Datos para asegurar datos en vivo
        df_ram_csv = df_steam_full[df_steam_full['categoria']=='RAM'].sort_values('global_share_percentage', ascending=True)
        df_ram_csv = df_ram_csv.rename(columns={'global_share_percentage':'percentage'})

        fig_ram = px.bar(
            df_ram_csv, x='percentage', y='name', orientation='h',
            text=df_ram_csv['percentage'].apply(lambda x: f'{x*100:.1f}%' if x < 1 else f'{x:.1f}%'),
            color='percentage', color_continuous_scale='Blues',
            labels={'percentage':'% jugadores','name':''}
        )
        fig_ram.update_traces(textposition='outside')
        fig_ram.update_layout(height=280, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              margin=dict(r=80,l=0,t=10,b=0), coloraxis_showscale=False,
                              xaxis=dict(showticklabels=False))
        st.plotly_chart(fig_ram, use_container_width=True)


