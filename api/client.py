import requests
import base64
import os
import pandas as pd
from dotenv import load_dotenv

# Cargar variables desde api/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

APP_ID  = os.getenv("EBAY_APP_ID")
CERT_ID = os.getenv("EBAY_CERT_ID")

def get_token() -> str:
    if not APP_ID or not CERT_ID:
        raise ValueError("Faltan las credenciales de eBay en el archivo .env")
        
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
    if pd.isna(component) or not str(component).strip():
        return None
        
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
    }
    params = {"q": str(component), "limit": 5}
    
    try:
        res = requests.get(url, headers=headers, params=params).json()
        items = res.get("itemSummaries", [])
        
        if not items:
            return None
            
        prices = [float(item["price"]["value"]) for item in items if "price" in item]
        if not prices:
            return None
            
        return round(sum(prices) / len(prices), 2)
    except Exception as e:
        print(f"Error consultando {component}: {e}")
        return None

def obtener_valor_dolar() -> float:
    try:
        response = requests.get("https://mindicador.cl/api/dolar", timeout=5)
        return response.json()['serie'][0]['valor']
    except Exception:
        return 920.0