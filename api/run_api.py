import sys
import os

ruta_actual = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(ruta_actual))

from api.fetch_prices import procesar_precios

if __name__ == "__main__":
    print("Arrancando Pipeline de API eBay...")
    procesar_precios()
    print("Proceso finalizado.")