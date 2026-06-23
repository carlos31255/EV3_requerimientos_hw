# Documentación de la API de eBay

## Descripción
El módulo `api/` integra la **eBay Browse API v1** para obtener precios de mercado en tiempo real de los componentes de PC del catálogo. Adicionalmente consume la API pública de **mindicador.cl** para obtener el tipo de cambio USD → CLP.

---

## Autenticación — eBay OAuth2

Se utiliza el flujo **Client Credentials** (sin intervención del usuario), adecuado para consultas de catálogo público.

**Endpoint:**
```
POST https://api.ebay.com/identity/v1/oauth2/token
```

**Headers:**
```
Authorization: Basic base64(APP_ID:CERT_ID)
Content-Type: application/x-www-form-urlencoded
```

**Body:**
```
grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope
```

**Respuesta exitosa:**
```json
{
  "access_token": "v^1.1#i^1#r^0#...",
  "token_type": "Application Access Token",
  "expires_in": 7200
}
```

---

## Búsqueda de Precios — eBay Browse API

**Endpoint:**
```
GET https://api.ebay.com/buy/browse/v1/item_summary/search
```

**Headers:**
```
Authorization: Bearer {access_token}
X-EBAY-C-MARKETPLACE-ID: EBAY_US
```

**Parámetros:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `q` | string | Nombre del componente a buscar (ej: `RTX 3060`) |
| `limit` | int | Número de resultados (máximo 5 para evitar rate limiting) |

**Ejemplo de llamada:**
```python
params = {"q": "RTX 3060", "limit": 5}
res = requests.get(url, headers=headers, params=params).json()
```

**Extracción del precio promedio:**
```python
items = res.get("itemSummaries", [])
prices = [float(item["price"]["value"]) for item in items if "price" in item]
precio_promedio = round(sum(prices) / len(prices), 2)
```

---

## Tipo de Cambio — mindicador.cl

**Endpoint:**
```
GET https://mindicador.cl/api/dolar
```

**Respuesta:**
```json
{
  "serie": [{ "valor": 945.50, "fecha": "2026-06-22T..." }]
}
```

**Uso en el proyecto:**
```python
dolar_clp = response.json()['serie'][0]['valor']
precio_clp = int(precio_usd * dolar_clp)
```

---

## Optimizaciones Implementadas

### Caché en Memoria
Para evitar llamadas duplicadas (múltiples juegos pueden requerir la misma GPU):
```python
cache_precios = {}

if componente in cache_precios:
    precio = cache_precios[componente]   # Sin llamada a eBay
else:
    precio = get_price(componente, token)
    cache_precios[componente] = precio
```

### Multithreading
Las búsquedas se ejecutan en paralelo para reducir el tiempo total:
```python
with ThreadPoolExecutor(max_workers=2) as executor:
    futuros = {executor.submit(fetch_single_price, comp, token): comp for comp in a_buscar}
```

### Rate Limiting
Se añade un retardo de 0.5 segundos entre llamadas para no superar el límite de la API:
```python
time.sleep(0.5)
```

---

## Ejecución

```bash
# Desde la raíz del proyecto, con Docker corriendo:
python api/run_api.py
```

**Salida esperada:**
```
INFO  Dólar: $945.5 CLP
INFO  Buscando 12 componentes (GPU) en eBay...
INFO    RTX 3060: USD $289.5
INFO    GTX 1650: USD $129.0
INFO  BD actualizada: 10 precios guardados, 2 no mapeados.
```

---

## Manejo de Errores

| Situación | Comportamiento |
|---|---|
| Credenciales inválidas | Lanza `KeyError` al acceder al token; el proceso se detiene con mensaje claro |
| Componente no encontrado en eBay | Retorna `None`; no se inserta precio (no se usa 0) |
| mindicador.cl no responde | Fallback automático a `$920.0 CLP` por USD |
| MySQL no disponible | `SQLAlchemyError` capturado, muestra mensaje de error y sale limpiamente |
