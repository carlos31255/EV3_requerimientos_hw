"""
etl/clean_games.py
==================
Pipeline ETL para limpiar el dataset de requisitos de juegos de PC.
Fuente: Kaggle — baraazaid/pc-video-game-requirements

Transformaciones:
  1. Renombrar columnas a snake_case sin caracteres especiales
  2. Limpiar 'game_name': eliminar sufijo ' System Requirements'
  3. Strip de espacios en blanco en todos los campos de texto
  4. Normalizar 'Unknown' y variantes a NaN
  5. Eliminar filas donde TODOS los campos de hardware son nulos

Entrada : data/kaggle/PC_video_games_requirements.csv
Salida  : data/kaggle/games_clean.csv
"""

import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────
# Rutas
# ─────────────────────────────────────────────
INPUT  = Path("data/kaggle/PC_video_games_requirements.csv")
OUTPUT = Path("data/kaggle/games_clean.csv")

# ─────────────────────────────────────────────
# Carga
# ─────────────────────────────────────────────
print("Cargando dataset...")
df = pd.read_csv(INPUT)
print(f"  Filas originales : {len(df):,}")

# ─────────────────────────────────────────────
# 1. Renombrar columnas
# ─────────────────────────────────────────────
df = df.rename(columns={
    "name"           : "game_name",
    "Memory:"        : "ram",
    "Graphics Card:" : "gpu",
    "CPU:"           : "cpu",
    "File Size:"     : "storage",
    "OS:"            : "os",
})

# ─────────────────────────────────────────────
# 2. Strip de espacios en todos los strings
# ─────────────────────────────────────────────
str_cols = ["game_name", "ram", "gpu", "cpu", "storage", "os"]
for col in str_cols:
    df[col] = df[col].astype(str).str.strip()

# ─────────────────────────────────────────────
# 3. Limpiar nombre del juego
# ─────────────────────────────────────────────
df["game_name"] = df["game_name"].str.replace(
    r"\s*System Requirements\s*$", "", regex=True
).str.strip()

# ─────────────────────────────────────────────
# 4. Normalizar 'Unknown' y 'nan' → NaN
# ─────────────────────────────────────────────
hw_cols = ["ram", "gpu", "cpu", "storage", "os"]
for col in hw_cols:
    df[col] = df[col].replace(
        to_replace=r"(?i)^(unknown|nan)$", value=pd.NA, regex=True
    )

# ─────────────────────────────────────────────
# 5. Eliminar filas con TODOS los campos de hardware nulos
# ─────────────────────────────────────────────
before = len(df)
df = df.dropna(subset=hw_cols, how="all")
dropped = before - len(df)
print(f"  Filas eliminadas (todo nulo): {dropped:,}")

# ─────────────────────────────────────────────
# 6. Reordenar columnas
# ─────────────────────────────────────────────
df = df[["game_name", "cpu", "ram", "gpu", "storage", "os"]]

# ─────────────────────────────────────────────
# Guardar
# ─────────────────────────────────────────────
df.to_csv(OUTPUT, index=False, encoding="utf-8")

print(f"  Filas finales    : {len(df):,}")
print()
print("Nulos por columna:")
print(df.isnull().sum().to_string())
print()
print(f"Guardado en: {OUTPUT}")
print("Limpieza completada.")
