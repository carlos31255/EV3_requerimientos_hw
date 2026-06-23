# Instrucciones — Rama `api`

Tu tarea es conectar la API de **eBay** para obtener precios reales de componentes de PC y llenar el dataset integrado que dejó el ETL.

---

## Input

```
data/integrated/requirements_market.csv
```

Este archivo tiene **80,575 juegos** con sus requisitos de hardware. Las siguientes columnas están **vacías** y las debes llenar:

| Columna | Descripción |
|---|---|
| `price_cpu_usd` | Precio del CPU requerido |
| `price_ram_usd` | Precio del kit de RAM requerido |
| `price_gpu_usd` | Precio de la GPU requerida |
| `price_storage_usd` | Precio del almacenamiento requerido |
| `total_upgrade_usd` | **Suma de los anteriores** (calcúlalo tú) |

---

## Columnas nuevas del ETL que te ayudan

El ETL ahora incluye dos columnas adicionales que debes usar para guiar las búsquedas en eBay:

| Columna | Valores posibles | Uso |
|---|---|---|
| `gpu_tier` | `ultra / high / mid / low / integrated / legacy / unknown` | Nivel de rendimiento de la GPU requerida |
| `gpu_match_status` | `found / legacy / unknown` | Indica si la GPU existe en la Steam HW Survey actual |

### Lógica de búsqueda de GPU en eBay

No busques el nombre exacto de GPU siempre — muchas son obsoletas y no aparecerán con precio útil:

| `gpu_match_status` | Qué buscar en eBay |
|---|---|
| `found` | El nombre exacto de la columna `gpu` |
| `legacy` | Un sustituto moderno según `gpu_tier` (ver tabla abajo) |
| `unknown` | Un sustituto genérico por tier, o dejar `null` |

### Tabla de sustitutos para GPUs legacy

| `gpu_tier` | Query sugerida en eBay |
|---|---|
| `ultra` | `"RTX 4090"` |
| `high` | `"RTX 3070"` |
| `mid` | `"RTX 3060"` |
| `low` | `"GTX 1650"` |
| `integrated` | Dejar `null` (GPU integrada, no se actualiza) |
| `unknown` | Dejar `null` |

---

## Lo que ya tienes funcionando

En `tests/test_ebay.py` ya tienes implementado y probado:

- `get_token()` — autenticación OAuth2 con eBay (Production)
- `get_price(component, token)` — consulta la Browse API v1, devuelve precio promedio USD
- `obtener_valor_dolar()` — tipo de cambio USD → CLP via mindicador.cl

**Mueve esas funciones a `api/` como módulo limpio.**

---

## Estructura sugerida para `api/`

```
api/
├── client.py        # get_token(), get_price(), get_dolar_clp()
├── cache.py         # Caché {query: precio_usd} para evitar llamadas repetidas
├── fetch_prices.py  # Lee el CSV, consulta eBay por cada componente, guarda resultado
└── run_api.py       # Punto de entrada: python api/run_api.py
```

> **Importante — usa caché.** Hay 80K juegos pero muchos repiten la misma GPU o CPU (ej. 15,000 juegos piden `ATI FireGL T2-128`). Sin caché harías miles de llamadas idénticas y llegarías al rate limit de eBay.

---

## Cómo validar tu output

El esquema esperado ya está definido en `etl/schemas.py → PARTPICKER_SCHEMA`.

```python
from etl.schemas import PARTPICKER_SCHEMA
from etl.validate import validate_dataframe
import logging

logger = logging.getLogger("api")
df_precios, report = validate_dataframe(df_precios, PARTPICKER_SCHEMA, logger)
```

Reglas que se verifican automáticamente:
- `component_type` debe ser: `GPU`, `CPU`, `RAM`, `SSD` o `HDD`
- `price_usd` debe ser mayor a 0
- `component_type` y `name` no pueden ser nulos

---

## Output esperado

El mismo archivo con las columnas de precio rellenas:

```
data/integrated/requirements_market.csv  (actualizado)
```

---

## Notas adicionales

- Los precios son en **USD**. La conversión a CLP es opcional (usar `obtener_valor_dolar()`).
- Si eBay no devuelve resultados para una query, deja la columna como `null` — no pongas 0.
- `total_upgrade_usd` = suma de las 4 columnas de precio (ignorando nulls).
- Coordina con el ETL si necesitas que se agregue alguna columna adicional al dataset.
