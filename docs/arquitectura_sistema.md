# Documentación Técnica — Sistema de Inteligencia de Hardware para Gaming

## Descripción General

Sistema de análisis y recomendación de componentes de PC para gaming, desarrollado como proyecto de Ciencia de Datos (EV3). Integra tres fuentes de datos externas en un Data Warehouse MySQL, expuesto mediante un dashboard interactivo en Streamlit.

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FUENTES DE DATOS                         │
│                                                             │
│  [Kaggle CSV]  [Steam HW Survey]  [eBay API]               │
└──────┬──────────────┬──────────────────┬────────────────────┘
       │              │                  │
       ▼              ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA ETL                                 │
│                                                             │
│  etl/extraer_muestra.py     api/fetch_prices.py            │
│  (limpieza y muestreo)      (consulta eBay → BD)           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              DATA WAREHOUSE  (MySQL en Docker)              │
│                                                             │
│  component          game_requeriments   market_prices_ext. │
│  component_tiers    games               steam_hardware_surv │
│  build_templates    store_inventory     build_components    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              DASHBOARD  (Streamlit en Docker)               │
│                                                             │
│  Vista Ejecutiva  │  Vista Técnica  │  Vista Operativa     │
└─────────────────────────────────────────────────────────────┘
```

---

## Fuentes de Datos

### 1. Kaggle — Requisitos de Juegos
- **Archivo:** `data/kaggle/PC_video_games_requirements.csv`
- **Contenido:** Requisitos mínimos de hardware de miles de juegos de PC.
- **ETL:** `etl/extraer_muestra.py` extrae una muestra representativa de 15 juegos y genera `data/kaggle/games_sample_15.csv`.
- **Carga en BD:** Los juegos y sus requisitos (mínimos y recomendados) se cargan en las tablas `games` y `game_requeriments`.

### 2. Steam Hardware Survey
- **Archivo:** `data/steamhwsurvey/steam_sample_15.csv`
- **Contenido:** Distribución de hardware real entre los jugadores activos de Steam (GPU, CPU, RAM, almacenamiento).
- **ETL:** `etl/extraer_muestra.py` genera la muestra desde el dataset completo (ignorado por `.gitignore` por su tamaño).
- **Carga en BD:** Se almacena en `steam_hardware_survey` relacionada con el catálogo `component`.

### 3. eBay API (Precios de Mercado)
- **Script:** `api/fetch_prices.py`
- **Autenticación:** OAuth2 Client Credentials (Production), credenciales en `api/.env` (no subido al repo).
- **Lógica:**
  1. Lee los componentes únicos de los CSVs de juegos y Steam.
  2. Busca el precio promedio de cada componente en eBay Browse API v1 (`limit: 5 resultados`).
  3. Convierte USD → CLP usando la API de mindicador.cl.
  4. Guarda los resultados en la tabla `market_prices_external` usando UPSERT.
- **Optimizaciones:** Caché en memoria y multithreading (`ThreadPoolExecutor`, `max_workers=2`) para evitar rate limiting.

---

## Base de Datos

### Servidor
- Motor: **MySQL 8.0** en contenedor Docker.
- Puerto local: **3307** (para no conflictar con instalaciones locales de MySQL).
- Usuario: `root` / Contraseña: `mysql`.

### Tablas principales

| Tabla | Descripción |
|---|---|
| `component` | Catálogo maestro de componentes (GPU, CPU, RAM, Storage) |
| `component_tiers` | Clasificación por gama (Baja, Media, Alta) |
| `market_prices_external` | Precios USD/CLP desde eBay |
| `games` | 15 juegos seleccionados del dataset de Kaggle |
| `game_requeriments` | Requisitos mínimos y recomendados por juego |
| `steam_hardware_survey` | Distribución de uso de hardware en Steam |
| `build_templates` | Builds de PC predefinidos por la tienda |
| `store_inventory` | Inventario y precios propios de la tienda |

### Inicialización
```bash
# Los contenedores generan la BD automáticamente al arrancar
docker-compose up -d
```

---

## Módulo API (`api/`)

| Archivo | Responsabilidad |
|---|---|
| `client.py` | Autenticación eBay (`get_token`), consulta de precios (`get_price`), tipo de cambio (`obtener_valor_dolar`) |
| `fetch_prices.py` | Motor ETL: lee CSVs → eBay → guarda en BD |
| `run_api.py` | Punto de entrada: `python api/run_api.py` |

### Configuración de credenciales
Crear el archivo `api/.env` (no subir al repositorio) con:
```env
EBAY_APP_ID=tu_app_id
EBAY_CERT_ID=tu_cert_id
```

### Ejecución
```bash
# Con el contenedor Docker corriendo:
python api/run_api.py
```

---

## Dashboard (`dashboards/app.py`)

### Vista Ejecutiva 👔
Orientada a gerencia. Muestra KPIs de mercado, análisis de precios por categoría y uso de hardware según la encuesta de Steam. Los gráficos son filtrables por categoría en tiempo real.

### Vista Técnica 🔧
Orientada a ingenieros y analistas. Muestra los requisitos mínimos y recomendados por juego (leídos desde la BD), distribución de RAM por juego y las GPUs más exigidas por los títulos del catálogo.

### Vista Operativa 🛒
Orientada a la tienda. Recomendador de builds (Gama Baja / Media / Alta) que calcula el costo total de cada pieza y lo contrasta con el precio de inventario propio.

---

## Despliegue Local

### Requisitos
- Docker Desktop
- Python 3.11+
- Credenciales de eBay (para actualizar precios)

### Pasos
```bash
# 1. Clonar el repositorio
git clone https://github.com/carlos31255/EV3_requerimientos_hw

# 2. Iniciar el sistema completo
./iniciar_proyecto.bat     # Windows

# 3. (Opcional) Actualizar precios desde eBay
python api/run_api.py

# 4. Acceder al dashboard
# http://localhost:8501
```

---

## Estructura de Carpetas

```
EV3/
├── api/                ← Integración con la API de eBay
├── dashboards/         ← Frontend Streamlit
├── data/
│   ├── kaggle/         ← Dataset de requisitos de juegos
│   └── steamhwsurvey/  ← Datos de la encuesta Steam
├── db/                 ← Scripts SQL (schema + datos iniciales)
├── eda/                ← Análisis exploratorio (Jupyter)
├── etl/                ← Scripts de extracción y transformación
├── tests/              ← Pruebas del crawler de Steam
├── docker-compose.yml
├── Dockerfile
└── iniciar_proyecto.bat
```

---

## Tecnologías Utilizadas

| Categoría | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Dashboard | Streamlit |
| Base de Datos | MySQL 8.0 |
| Contenedores | Docker / Docker Compose |
| APIs externas | eBay Browse API v1, mindicador.cl |
| Librerías | pandas, plotly, sqlalchemy, pymysql, requests |
| Datasets | Kaggle (PC Video Games Requirements), Steam HW Survey |
