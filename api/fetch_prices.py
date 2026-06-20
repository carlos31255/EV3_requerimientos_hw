import pandas as pd
import sys
import os
import time
import logging
import concurrent.futures  # MULTITHREADING

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_actual)
sys.path.append(ruta_raiz)

from api.client import get_token, get_price

try:
    from etl.schemas import PARTPICKER_SCHEMA
    from etl.validate import validate_dataframe
except ImportError:
    pass

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)

def determinar_query_gpu(row):
    """Aplica la regla de negocio para sustituir GPUs obsoletas"""
    status = row.get('gpu_match_status')
    tier = row.get('gpu_tier')
    nombre_original = row.get('gpu') 
    
    if pd.isna(status) or status == 'unknown' or tier == 'integrated':
        return None
        
    if status == 'found':
        return nombre_original
        
    if status == 'legacy':
        sustitutos = {
            'ultra': 'RTX 4090',
            'high': 'RTX 3070',
            'mid': 'RTX 3060',
            'low': 'GTX 1650'
        }
        return sustitutos.get(tier, None)
        
    return None

def fetch_single_price(comp, token):
    """Función de trabajo aislada para que la ejecute cada hilo."""
    print(f"Buscando en eBay: {comp}")
    precio = get_price(comp, token)
    # Una micro-pausa de 0.5s para no martillar el servidor tan violentamente
    time.sleep(0.5) 
    return comp, precio

def procesar_precios():
    csv_path = os.path.join(ruta_raiz, "data", "integrated", "requirements_market.csv")
    logger.info(f"Cargando dataset desde {csv_path}...")
    df = pd.read_csv(csv_path)

    # Aplicar la lógica de GPU
    df['gpu_search_query'] = df.apply(determinar_query_gpu, axis=1)

    # caché
    cols_buscar = {
        'CPU': df['cpu'].dropna().unique(),
        'GPU': df['gpu_search_query'].dropna().unique(),
        'RAM': df['ram'].dropna().unique(),
        'SSD': df['storage'].dropna().unique()
    }

    token = get_token()
    cache_precios = {}
    datos_validador = []

    # Consultar ebay usando el caché con multithreading
    logger.info("Iniciando consultas a eBay...")
    
    # NO AUMENTAR o se cae
    MAX_WORKERS = 2

    for tipo_comp, componentes_unicos in cols_buscar.items():
        logger.info(f" Procesando {len(componentes_unicos)} componentes de tipo {tipo_comp} con {MAX_WORKERS} trabajadores...") 
        
        a_buscar = [c for c in componentes_unicos if c not in cache_precios]

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Asignamos todas las tareas al pool de trabajadores
            futuros = {executor.submit(fetch_single_price, comp, token): comp for comp in a_buscar}
            
            # as_completed nos va entregando los resultados a medida que cada trabajador termina
            for futuro in concurrent.futures.as_completed(futuros):
                comp = futuros[futuro]
                try:
                    # Recuperamos la respuesta del trabajador
                    comp_resultado, precio = futuro.result()
                    
                    # Guardamos de forma segura y secuencial
                    cache_precios[comp_resultado] = precio
                    
                    if precio is not None and precio > 0:
                        datos_validador.append({
                            "component_type": tipo_comp,
                            "name": comp_resultado,
                            "price_usd": precio
                        })
                except Exception as exc:
                    logger.error(f"Error en el hilo procesando {comp}: {exc}")

    # Validar el esquema
    df_precios_unicos = pd.DataFrame(datos_validador, columns=["component_type", "name", "price_usd"])
    
    logger.info("Validando esquema de precios...")
    if df_precios_unicos.empty:
        logger.warning("No se encontraron precios válidos para validar.")
    else:
        try:
            df_precios_unicos, report = validate_dataframe(df_precios_unicos, PARTPICKER_SCHEMA, logger)
        except NameError:
            logger.warning("El validador no está disponible. Saltando validación.")

    # Mapear los precios desde el caché de vuelta al dataset 
    logger.info("Inyectando precios al dataset...")
    df['price_cpu_usd'] = df['cpu'].map(cache_precios)
    df['price_gpu_usd'] = df['gpu_search_query'].map(cache_precios)
    df['price_ram_usd'] = df['ram'].map(cache_precios)
    df['price_storage_usd'] = df['storage'].map(cache_precios)

    # Calcular total ignorando los nulls
    columnas_precio = ['price_cpu_usd', 'price_gpu_usd', 'price_ram_usd', 'price_storage_usd']
    df['total_upgrade_usd'] = df[columnas_precio].sum(axis=1, skipna=True, min_count=1)

    df.drop(columns=['gpu_search_query'], inplace=True)

    # Guardar resultados
    df.to_csv(csv_path, index=False)
    logger.info("¡Dataset actualizado exitosamente con los precios de eBay!")

if __name__ == "__main__":
    procesar_precios()