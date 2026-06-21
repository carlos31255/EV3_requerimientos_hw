import sys
import os

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.dirname(ruta_actual)
sys.path.append(ruta_raiz)

from api.fetch_prices import procesar_ambos_archivos

if __name__ == "__main__":
    print("Arrancando Pipeline de API eBay...\n")
    
    procesar_ambos_archivos()
    
    
    print("¡PIPELINE EJECUTADO CON ÉXITO!")
    print("Todos los precios de eBay han sido procesados y guardados.")
