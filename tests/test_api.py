# Este es un script de testing automatizado al crawler de Steam
# Testea la actualización en vivo de steam con intervalos de 60 segundos

import time
import os
import pandas as pd
from datetime import datetime
import sys

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_actual)


ruta_libreria = os.path.join(ruta_raiz, "data", "steamhwsurvey")

sys.path.append(ruta_libreria)

import steamHWScrawler



def extraer_datos():
    """
    Función que ejecuta el scraper de Steam y lee el resultado.
    """
    archivo_prueba = "test_shs.csv"
    
    try:
        steamHWScrawler.update_month_current_steam(out_csv_path=archivo_prueba)
        
        if os.path.exists(archivo_prueba):
            df = pd.read_csv(archivo_prueba)
            
            os.remove(archivo_prueba) 
            
            return df.to_string() 
        else:
            return None
            
    except Exception as e:
        print(f"Error al consultar la página: {e}")
        return None

def testear_actualizacion(intentos=3, espera_segundos=60):
    print("Iniciando test de actualización del crawler de Steam...")
    
    datos_anteriores = None
    
    for i in range(1, intentos + 1):
        hora_actual = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{hora_actual}] Ejecutando intento {i}/{intentos}...")
        
        datos_actuales = extraer_datos()
        
        if datos_actuales is None:
            print("No se pudieron obtener datos en este intento.")
            continue
            
        if datos_anteriores is None:
            print("Primera carga exitosa. Guardando foto de los datos para comparar...")
        elif datos_actuales != datos_anteriores:
            print("Los datos cambiaron respecto a la consulta anterior. La actualización funciona.")
        else:
            print("Los datos son IDÉNTICOS. O la página de Steam no ha cambiado en este minuto, o están usando caché.")
            
        datos_anteriores = datos_actuales
        
        if i < intentos:
            print(f"Pausa táctica de {espera_segundos} segundos...")
            time.sleep(espera_segundos)
            
    print("\nTest finalizado.")

if __name__ == "__main__":
    testear_actualizacion(intentos=3, espera_segundos=60)