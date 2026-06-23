import pandas as pd
import sys
import os
import time
import logging
import concurrent.futures
from sqlalchemy import create_engine, text

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_actual)
sys.path.append(ruta_raiz)

from api.client import get_token, get_price, obtener_valor_dolar

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Conexión a la BD (mismo config que usa el dashboard)
DB_USER = "root"
DB_PASS = "mysql"
DB_HOST = "localhost"
DB_PORT = "3307"
DB_NAME = "tienda_hardware_intelligence"

def fetch_single_price(comp, token):
    precio = get_price(comp, token)
    time.sleep(0.5)  # Velocidad segura para no superar el rate limit
    return comp, precio

def procesar_ambos_archivos():
    token = get_token()
    if not token:
        logger.error("No se pudo obtener token de eBay. Verifica tus credenciales.")
        return

    dolar_clp = obtener_valor_dolar()
    logger.info(f"Dólar: ${dolar_clp} CLP")

    cache_precios = {}
    MAX_WORKERS = 2

    archivos_a_procesar = ["games", "steam"]

    for tipo_archivo in archivos_a_procesar:
        logger.info(f"--- PROCESANDO: {tipo_archivo.upper()} ---")

        if tipo_archivo == "games":
            ruta_entrada = os.path.join(ruta_raiz, "data", "kaggle", "games_sample_15.csv")
            df = pd.read_csv(ruta_entrada)
            cols_buscar = {
                'CPU': df['cpu'].dropna().unique(),
                'GPU': df['gpu'].dropna().unique(),
                'RAM': df['ram'].dropna().unique(),
                'SSD': df['storage'].dropna().unique()
            }

        elif tipo_archivo == "steam":
            ruta_entrada = os.path.join(ruta_raiz, "data", "steamhwsurvey", "steam_sample_15.csv")
            df = pd.read_csv(ruta_entrada)
            nombre_col = 'name'
            if nombre_col not in df.columns:
                logger.error(f"Columna '{nombre_col}' no existe en Steam CSV.")
                continue
            cols_buscar = {'GPU': df[nombre_col].dropna().unique()}

        # Buscar precios en eBay con caché y multithreading
        for tipo_comp, componentes_unicos in cols_buscar.items():
            a_buscar = [c for c in componentes_unicos if c not in cache_precios]
            if a_buscar:
                logger.info(f"Buscando {len(a_buscar)} componentes ({tipo_comp}) en eBay...")
                with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    futuros = {executor.submit(fetch_single_price, comp, token): comp for comp in a_buscar}
                    for futuro in concurrent.futures.as_completed(futuros):
                        comp = futuros[futuro]
                        try:
                            comp_resultado, precio = futuro.result()
                            cache_precios[comp_resultado] = precio if precio is not None else None
                            logger.info(f"  {comp_resultado}: {'USD $' + str(precio) if precio else 'No encontrado'}")
                        except Exception as exc:
                            logger.error(f"Error procesando {comp}: {exc}")
            else:
                logger.info(f"Todos los {tipo_comp} ya están en caché.")

    # Guardar precios en la Base de Datos
    _guardar_en_bd(cache_precios, dolar_clp)


def _guardar_en_bd(cache_precios: dict, dolar_clp: float):
    """Actualiza la tabla market_prices_external con los precios reales de eBay."""
    try:
        engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        exitos = 0
        fallos = 0

        with engine.connect() as conn:
            # Obtener el catálogo de componentes para mapear nombres a IDs
            result = conn.execute(text("SELECT id, name FROM component"))
            catalogo = {row[1]: row[0] for row in result.fetchall()}

            for comp_name, precio_usd in cache_precios.items():
                if comp_name not in catalogo or precio_usd is None:
                    fallos += 1
                    continue

                comp_id = catalogo[comp_name]
                precio_clp = int(precio_usd * dolar_clp)
                url = f"https://www.ebay.com/sch/i.html?_nkw={comp_name.replace(' ', '+')}"

                # Upsert: actualizar si ya existe, insertar si no
                conn.execute(text("""
                    INSERT INTO market_prices_external (component_id, price_usd, price_clp, source_url)
                    VALUES (:cid, :pusd, :pclp, :url)
                    ON DUPLICATE KEY UPDATE
                        price_usd = VALUES(price_usd),
                        price_clp = VALUES(price_clp),
                        source_url = VALUES(source_url)
                """), {"cid": comp_id, "pusd": precio_usd, "pclp": precio_clp, "url": url})
                exitos += 1

            conn.commit()

        logger.info(f"BD actualizada: {exitos} precios guardados, {fallos} no mapeados.")

    except Exception as e:
        logger.error(f"Error al guardar en la BD: {e}")


if __name__ == "__main__":
    procesar_ambos_archivos()