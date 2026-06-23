import pandas as pd
import sys
import os
import time
import logging
import concurrent.futures

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_actual)
sys.path.append(ruta_raiz)

from api.client import get_token, get_price

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)

def fetch_single_price(comp, token):
    print(f"Buscando en eBay: {comp}")
    precio = get_price(comp, token)
    time.sleep(0.5) # Velocidad segura
    return comp, precio

def procesar_ambos_archivos():
    token = get_token()
    
    cache_precios = {} 
    MAX_WORKERS = 2 

    archivos_a_procesar = ["games", "steam"]

    for tipo_archivo in archivos_a_procesar:
        logger.info(f"INICIANDO PROCESAMIENTO DE: {tipo_archivo.upper()}")
        
        if tipo_archivo == "games":
            ruta_entrada = os.path.join(ruta_raiz, "data", "kaggle", "games_sample_15.csv")
            ruta_salida = os.path.join(ruta_raiz, "data", "kaggle", "games_sample_15_PRICED.csv")
            
            logger.info(f"Cargando dataset desde {ruta_entrada}...")
            df = pd.read_csv(ruta_entrada, on_bad_lines='skip')

            cols_buscar = {
                'CPU': df['cpu'].dropna().unique(),
                'GPU': df['gpu'].dropna().unique(),
                'RAM': df['ram'].dropna().unique(),
                'SSD': df['storage'].dropna().unique()
            }

        elif tipo_archivo == "steam":
            ruta_entrada = os.path.join(ruta_raiz, "data", "steamhwsurvey", "steam_sample_15.csv")
            ruta_salida = os.path.join(ruta_raiz, "data", "steamhwsurvey", "steam_sample_15_PRICED.csv")
            
            logger.info(f"Cargando dataset desde {ruta_entrada}...")
            df = pd.read_csv(ruta_entrada)

            nombre_columna_steam = 'name' 
            
            if nombre_columna_steam not in df.columns:
                logger.error(f"La columna '{nombre_columna_steam}' no existe en Steam. Saltando archivo...")
                continue

            cols_buscar = {
                'GPU': df[nombre_columna_steam].dropna().unique()
            }

        # 2. BÚSQUEDA MULTITHREADING PARA ESTE ARCHIVO
        for tipo_comp, componentes_unicos in cols_buscar.items():
            logger.info(f"Procesando componentes de tipo {tipo_comp}...") 
            
            a_buscar = [c for c in componentes_unicos if c not in cache_precios]

            if a_buscar:
                logger.info(f"   (Buscando {len(a_buscar)} componentes nuevos en internet...)")
                with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    futuros = {executor.submit(fetch_single_price, comp, token): comp for comp in a_buscar}
                    
                    for futuro in concurrent.futures.as_completed(futuros):
                        comp = futuros[futuro]
                        try:
                            comp_resultado, precio = futuro.result()
                            cache_precios[comp_resultado] = precio if precio is not None else 0.0
                        except Exception as exc:
                            logger.error(f"Error procesando {comp}: {exc}")
            else:
                logger.info("Todos los componentes de este tipo ya estaban en caché.")

        # 3. MAPEO E INYECCIÓN
        logger.info("Inyectando precios al dataset...")
        if tipo_archivo == "games":
            df['price_cpu_usd'] = df['cpu'].map(cache_precios).fillna(0.0)
            df['price_gpu_usd'] = df['gpu'].map(cache_precios).fillna(0.0)
            df['price_ram_usd'] = df['ram'].map(cache_precios).fillna(0.0)
            df['price_storage_usd'] = df['storage'].map(cache_precios).fillna(0.0)
            
            df['total_upgrade_usd'] = (
                df['price_cpu_usd'] + df['price_gpu_usd'] + 
                df['price_ram_usd'] + df['price_storage_usd']
            )
        elif tipo_archivo == "steam":
            df['price_usd'] = df[nombre_columna_steam].map(cache_precios).fillna(0.0)

        # 4. GUARDADO
        df.to_csv