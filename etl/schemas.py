"""
etl/schemas.py
==============
Definicion de esquemas esperados para cada fuente de datos del pipeline.
La validacion se realiza con pandas puro (sin dependencias externas).

Cada esquema es un diccionario con:
  - required_columns : columnas que deben existir
  - non_null_columns : columnas que no pueden ser completamente nulas
  - dtype_checks     : {columna: tipo_esperado} (comprobacion flexible)
  - value_constraints: reglas de negocio adicionales (listas de funciones)
"""

# ─────────────────────────────────────────────────────────────────
# Esquema 1: dataset limpio de requisitos de juegos (Kaggle)
# ─────────────────────────────────────────────────────────────────
GAMES_SCHEMA = {
    "source": "Kaggle — PC Video Game Requirements",
    "required_columns": ["game_name", "cpu", "ram", "gpu", "storage", "os"],
    "non_null_columns": ["game_name"],   # al menos el nombre siempre debe existir
    "dtype_checks": {
        # pandas puede reportar 'object' o 'str' para columnas de texto — ambos son validos
    },
    "value_constraints": [
        # game_name no debe estar en blanco
        {
            "column": "game_name",
            "description": "game_name no debe contener cadenas vacias",
            "check": lambda df: df["game_name"].str.strip().ne(""),
        },
    ],
}

# ─────────────────────────────────────────────────────────────────
# Esquema 2: Steam Hardware Survey filtrada (pc + linux)
# ─────────────────────────────────────────────────────────────────
STEAM_SCHEMA = {
    "source": "Steam Hardware Survey — jdegene/steamHWsurvey",
    "required_columns": ["date", "platform", "category", "name", "change", "percentage"],
    "non_null_columns": ["date", "platform", "category", "name", "percentage"],
    "dtype_checks": {
        # solo verificamos tipos numericos; strings son 'object'/'str' indistintamente
        "change":     "float64",
        "percentage": "float64",
    },
    "value_constraints": [
        # platform solo puede ser 'pc' o 'linux' (ya filtramos mac)
        {
            "column": "platform",
            "description": "platform debe ser 'pc' o 'linux'",
            "check": lambda df: df["platform"].isin(["pc", "linux"]),
        },
        # percentage entre 0 y 1
        {
            "column": "percentage",
            "description": "percentage debe estar entre 0 y 1",
            "check": lambda df: df["percentage"].between(0, 1),
        },
    ],
}

# ─────────────────────────────────────────────────────────────────
# Esquema 3: precios de componentes (stub — lo llena la rama api)
# ─────────────────────────────────────────────────────────────────
PARTPICKER_SCHEMA = {
    "source": "PCPartPicker — PyPartPicker (stub ETL, precios reales via API)",
    "required_columns": ["component_type", "name", "price_usd"],
    "non_null_columns": ["component_type", "name"],
    "dtype_checks": {
        # solo verificamos el tipo numerico del precio
        "price_usd": "float64",
    },
    "value_constraints": [
        {
            "column": "component_type",
            "description": "component_type debe ser GPU, CPU, RAM, SSD o HDD",
            "check": lambda df: df["component_type"].isin(["GPU", "CPU", "RAM", "SSD", "HDD"]),
        },
        {
            "column": "price_usd",
            "description": "price_usd debe ser mayor que 0 cuando no es nulo",
            "check": lambda df: df["price_usd"].isna() | df["price_usd"].gt(0),
        },
    ],
}
