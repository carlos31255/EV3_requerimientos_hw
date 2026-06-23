# Guía de Despliegue y Manual de Usuario

## Requisitos Previos

| Herramienta | Versión mínima | Verificación |
|---|---|---|
| Docker Desktop | 4.x | `docker --version` |
| Python | 3.11+ | `python --version` |
| Git | 2.x | `git --version` |

---

## Instalación y Despliegue

### Opción A — Despliegue con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/carlos31255/EV3_requerimientos_hw.git
cd EV3_requerimientos_hw

# 2. Iniciar el sistema completo (MySQL + Streamlit)
iniciar_proyecto.bat        # Windows
# O bien manualmente:
docker-compose up -d

# 3. Acceder al dashboard
# Abrir en el navegador: http://localhost:8501

# 4. Apagar el sistema
apagar_proyecto.bat
# O bien:
docker-compose down
```

> El primer arranque puede tardar 30-60 segundos mientras MySQL inicializa la base de datos y carga los datos automáticamente desde `database/BD.sql` y `database/datos_BD.sql`.

---

### Opción B — Ejecución local sin Docker

```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el dashboard (requiere MySQL local en puerto 3307)
streamlit run dashboards/app.py
```

---

## Actualizar los Datos del Proyecto

### Re-ejecutar el ETL (requiere los datasets crudos)
```bash
# Genera games_sample_15.csv y steam_sample_15.csv
python etl/extraer_muestra.py

# Los logs quedan en logs/etl.log
```

### Actualizar precios desde eBay
```bash
# Crear api/.env con tus credenciales:
# EBAY_APP_ID=tu_app_id
# EBAY_CERT_ID=tu_cert_id

# Ejecutar (requiere Docker corriendo):
python api/run_api.py
```

---

## Manual de Usuario del Dashboard

### Vista Ejecutiva 👔
**Audiencia:** Gerencia y toma de decisiones.

| Elemento | Descripción |
|---|---|
| KPIs superiores | Componentes catalogados, GPU y RAM más popular en Steam |
| Gráfico de precios | Seleccionar categoría (GPU/CPU/RAM/Storage/PSU) para ver precios de mercado vs tienda |
| Uso en Steam | Filtrar por categoría para ver el % de jugadores que usa cada componente |
| Distribución por gama | Cuántos componentes hay en Gama Baja/Media/Alta por categoría |

### Vista Técnica 🔧
**Audiencia:** Ingenieros y analistas de datos.

| Elemento | Descripción |
|---|---|
| Selector de juego | Desplegable con los 15 juegos del catálogo |
| Radio Mínimo/Recomendado | Alterna entre el perfil de hardware mínimo (720p 30fps) y recomendado (1080p 60fps) |
| RAM recomendada | Gráfico horizontal con GB de RAM por juego (perfil recomendado) |
| GPUs más exigidas | Frecuencia con que aparece cada GPU en los requisitos recomendados |
| Tabla completa | Todos los juegos × todos sus componentes en formato tabla |

### Vista Operativa 🛒
**Audiencia:** Personal de tienda y atención al cliente.

| Elemento | Descripción |
|---|---|
| Selector de Build | Elegir Gama Baja / Media / Alta |
| Lista de componentes | Piezas que conforman el build seleccionado |
| Precio de mercado vs tienda | Comparación automática para ver competitividad |
| Tabla de inventario | Stock y diferencia de precio (✅ Competitivo / ⚠️ Precio alto / 🚨 Muy caro) |

---

## Variables de Entorno

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `DB_HOST` | `localhost` | Host del servidor MySQL |
| `DB_PORT` | `3307` | Puerto del servidor MySQL |
| `DB_USER` | `root` | Usuario de la base de datos |
| `DB_PASSWORD` | `` (vacío) | Contraseña de la base de datos |
| `DB_NAME` | `tienda_hardware_intelligence` | Nombre de la base de datos |
| `EBAY_APP_ID` | — | App ID de la API de eBay (en `api/.env`) |
| `EBAY_CERT_ID` | — | Cert ID de la API de eBay (en `api/.env`) |

---

## Resolución de Problemas

| Problema | Solución |
|---|---|
| Dashboard no carga datos | Verificar que `ev3_mysql` esté `healthy` con `docker ps` |
| Puerto 8501 ocupado | Cambiar el puerto en `docker-compose.yml` y reiniciar |
| Error de conexión a eBay | Verificar que `api/.env` tiene credenciales válidas |
| ETL no encuentra el CSV de Steam | El archivo `steamHWsurvey/shs.csv` está ignorado por `.gitignore` por su tamaño. Descargarlo manualmente. |
