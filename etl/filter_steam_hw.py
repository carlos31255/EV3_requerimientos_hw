"""
etl/filter_steam_hw.py
======================
Pipeline ETL para la Steam Hardware Survey.

Filtra shs_platform.csv (descargado de jdegene/steamHWsurvey) para:
  - Eliminar datos de Mac (plataforma 'mac')
  - Conservar solo Windows ('pc') y Linux ('linux')
  - Quedarse con categorias de hardware relevantes para comparar
    requisitos de juegos (GPU, CPU, RAM, almacenamiento, SO)

Genera cuatro archivos en data/steamhwsurvey/:
  - shs_filtered.csv          : datos globales filtrados por categoria
  - shs_platform_filtered.csv : datos por plataforma pc+linux filtrados
  - shs_latest.csv            : snapshot del mes mas reciente (global)
  - shs_platform_latest.csv   : snapshot del mes mas reciente (pc+linux)

Fuente raw: data/steamhwsurvey/shs_platform.csv
"""

import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────
# Rutas
# ─────────────────────────────────────────────
DATA_DIR   = Path("data/steamhwsurvey")
INPUT_PLAT = DATA_DIR / "shs_platform.csv"   # raw con columna platform
INPUT_GLOB = DATA_DIR / "shs_filtered.csv"   # se regenera abajo desde steamHWsurvey/shs.csv si existe

# Fuentes alternativas (subcarpeta upstream de jdegene si existe)
INPUT_SHS  = Path("steamHWsurvey/shs.csv")

# ─────────────────────────────────────────────
# Categorias relevantes para comparar requisitos de juegos
# Coincidencia por substring para capturar variantes historicas
# ─────────────────────────────────────────────
RELEVANT_KEYWORDS = [
    "Video Card Description",   # GPU modelo
    "VRAM",                     # memoria de GPU
    "DirectX 12 GPUs",          # soporte DX12
    "DirectX 11 GPUs",          # soporte DX11
    "Vulkan",                   # soporte Vulkan
    "Physical CPUs",            # nucleos CPU
    "Processor Vendor",         # Intel / AMD
    "Intel CPU Speeds",         # velocidad CPU Intel
    "AMD CPU Speeds",           # velocidad CPU AMD
    "System RAM",               # memoria RAM
    "Drive Type",               # SSD vs HDD
    "Free Hard Drive Space",    # espacio libre
    "Total Hard Drive Space",   # espacio total
    "Primary Display Resolution",  # resolucion monitor
    "Windows Version",          # version de Windows
    "Linux Version",            # distribucion Linux
    "OS Version",               # version SO (global)
]

def is_relevant(category: str) -> bool:
    cat_lower = category.lower()
    return any(kw.lower() in cat_lower for kw in RELEVANT_KEYWORDS)


# ─────────────────────────────────────────────
# 1. Filtrar shs_platform.csv (pc + linux, sin mac)
# ─────────────────────────────────────────────
print("Cargando shs_platform.csv...")
df_plat = pd.read_csv(INPUT_PLAT, parse_dates=["date"])
print(f"  Filas originales : {len(df_plat):,}")
print(f"  Plataformas      : {df_plat['platform'].value_counts().to_dict()}")

# Eliminar Mac
df_no_mac = df_plat[df_plat["platform"].isin(["pc", "linux"])].copy()
print(f"  Tras eliminar Mac: {len(df_no_mac):,} filas")

# Filtrar categorias relevantes
df_plat_filtered = df_no_mac[df_no_mac["category"].apply(is_relevant)].copy()
print(f"  Tras filtro de categorias: {len(df_plat_filtered):,} filas")

out = DATA_DIR / "shs_platform_filtered.csv"
df_plat_filtered.to_csv(out, index=False)
print(f"  -> {out}")

# ─────────────────────────────────────────────
# 2. Filtrar shs.csv global (si existe)
# ─────────────────────────────────────────────
if INPUT_SHS.exists():
    print("\nCargando shs.csv (datos globales)...")
    df_glob = pd.read_csv(INPUT_SHS, parse_dates=["date"])
    df_glob_filtered = df_glob[df_glob["category"].apply(is_relevant)].copy()
    out_glob = DATA_DIR / "shs_filtered.csv"
    df_glob_filtered.to_csv(out_glob, index=False)
    print(f"  {len(df_glob):,} -> {len(df_glob_filtered):,} filas | -> {out_glob}")

    latest_global = df_glob_filtered["date"].max()
    df_glob_latest = df_glob_filtered[df_glob_filtered["date"] == latest_global]
    out_glob_latest = DATA_DIR / "shs_latest.csv"
    df_glob_latest.to_csv(out_glob_latest, index=False)
    print(f"  Snapshot {latest_global.strftime('%Y-%m')}: {len(df_glob_latest)} filas | -> {out_glob_latest}")
else:
    print("\nshs.csv no encontrado, omitiendo datos globales.")

# ─────────────────────────────────────────────
# 3. Snapshot del mes mas reciente (plataforma)
# ─────────────────────────────────────────────
latest_plat = df_plat_filtered["date"].max()
df_plat_latest = df_plat_filtered[df_plat_filtered["date"] == latest_plat].copy()
out_latest = DATA_DIR / "shs_platform_latest.csv"
df_plat_latest.to_csv(out_latest, index=False)
print(f"\nSnapshot mas reciente ({latest_plat.strftime('%Y-%m')}): {len(df_plat_latest)} filas | -> {out_latest}")

print("\nFiltrado completado.")
