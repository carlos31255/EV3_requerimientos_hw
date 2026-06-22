import requests
import base64
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# ─────────────────────────────────────────────
# Credenciales eBay — cargar desde variables de entorno
# Crea un archivo .env en la raiz del proyecto con:
#   EBAY_APP_ID=aqui_va_tu_app_id
#   EBAY_CERT_ID=aqui_va_tu_cert_id
# ─────────────────────────────────────────────
APP_ID  = os.getenv("EBAY_APP_ID")   # aqui va clave API
CERT_ID = os.getenv("EBAY_CERT_ID")  # aqui va clave API


def get_token() -> str:
    credentials = base64.b64encode(f"{APP_ID}:{CERT_ID}".encode()).decode()
    res = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data="grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope",
    )
    return res.json()["access_token"]


def get_price(component: str, token: str) -> float | None:
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
    }
    params = {"q": component, "limit": 5}
    res = requests.get(url, headers=headers, params=params).json()
    items = res.get("itemSummaries", [])

    if not items:
        return None

    prices = [float(item["price"]["value"]) for item in items if "price" in item]
    return round(sum(prices) / len(prices), 2)


def obtener_valor_dolar() -> float:
    try:
        response = requests.get("https://mindicador.cl/api/dolar", timeout=5)
        return response.json()['serie'][0]['valor']
    except Exception:
        return 920.0  # Valor por defecto si falla la conexion


if __name__ == "__main__":
    print("Prueba de eBay")

    token = get_token()
    dolar_clp = obtener_valor_dolar()

    componentes_prueba = ["RTX 3060", "Intel i5-12400"]

    for componente in componentes_prueba:
        precio_usd = get_price(componente, token)

        if precio_usd:
            precio_clp_entero = int(precio_usd * dolar_clp)
            precio_clp_formateado = f"{precio_clp_entero:,}".replace(",", ".")
            print(f"{componente}: USD ${precio_usd}    CLP aprox: ${precio_clp_formateado}")
        else:
            print(f"{componente}: Sin resultados en eBay.")
