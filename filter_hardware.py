"""
filter_hardware.py
==================
Filtra los CSVs de la Steam Hardware Survey para eliminar datos de Mac
y quedarse solo con Windows/Linux, enfocado en categorías relevantes
para un comparador de requisitos de juegos (GPU, CPU, RAM, almacenamiento).

Genera dos archivos filtrados:
  - shs_filtered.csv        : de shs.csv (datos globales, ya sin Mac por diseño)
  - shs_platform_filtered.csv : de shs_platform.csv (solo pc + linux)
"""

import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Categorías de hardware relevantes para comparar requisitos de juegos
# ---------------------------------------------------------------------------
# Usamos coincidencia por substring para capturar variantes históricas
# (ej. "System RAM (PC)", "System RAM (Windows)", etc.)
RELEVANT_CATEGORY_KEYWORDS = [
    # GPU / Tarjeta gráfica
    "Video Card Description",
    "VRAM",
    "DirectX 12 GPUs",
    "DirectX 11 GPUs",
    "Vulkan",
    # CPU
    "Physical CPUs",
    "Processor Vendor",
    "Intel CPU Speeds",
    "AMD CPU Speeds",
    # RAM
    "System RAM",
    # Almacenamiento
    "Drive Type",
    "Free Hard Drive Space",
    "Total Hard Drive Space",
    # Resolución / Monitor
    "Primary Display Resolution",
    # SO (para contexto)
    "Windows Version",
    "Linux Version",
    "OS Version",
]

def matches_relevant_category(category: str) -> bool:
    """Devuelve True si la categoría contiene alguna keyword relevante."""
    cat_lower = category.lower()
    return any(kw.lower() in cat_lower for kw in RELEVANT_CATEGORY_KEYWORDS)


# ---------------------------------------------------------------------------
# 1. Filtrar shs.csv (datos globales, sin columna platform)
# ---------------------------------------------------------------------------
print("Cargando shs.csv …")
shs = pd.read_csv("shs.csv", parse_dates=["date"])

print(f"  Filas originales : {len(shs):,}")

# shs.csv no tiene columna platform; ya representa datos globales (mayormente PC/Windows).
# Solo filtramos categorías relevantes.
shs_filtered = shs[shs["category"].apply(matches_relevant_category)].copy()

print(f"  Filas tras filtro de categorías: {len(shs_filtered):,}")
print(f"  Categorías conservadas: {sorted(shs_filtered['category'].unique())}")

shs_filtered.to_csv("shs_filtered.csv", index=False)
print("  → Guardado: shs_filtered.csv\n")


# ---------------------------------------------------------------------------
# 2. Filtrar shs_platform.csv (eliminar mac, conservar pc + linux)
# ---------------------------------------------------------------------------
print("Cargando shs_platform.csv …")
shs_plat = pd.read_csv("shs_platform.csv", parse_dates=["date"])

print(f"  Filas originales : {len(shs_plat):,}")
print(f"  Plataformas originales: {shs_plat['platform'].value_counts().to_dict()}")

# Eliminar Mac
shs_plat_no_mac = shs_plat[shs_plat["platform"].isin(["pc", "linux"])].copy()
print(f"  Filas tras eliminar Mac: {len(shs_plat_no_mac):,}")

# Filtrar categorías relevantes
shs_plat_filtered = shs_plat_no_mac[
    shs_plat_no_mac["category"].apply(matches_relevant_category)
].copy()

print(f"  Filas tras filtro de categorías: {len(shs_plat_filtered):,}")

# Resumen por plataforma y categoría
summary = (
    shs_plat_filtered
    .groupby(["platform", "category"])
    .size()
    .reset_index(name="rows")
    .sort_values(["platform", "category"])
)
print("\n  Resumen por plataforma y categoría:")
print(summary.to_string(index=False))

shs_plat_filtered.to_csv("shs_platform_filtered.csv", index=False)
print("\n  → Guardado: shs_platform_filtered.csv")


# ---------------------------------------------------------------------------
# 3. Snapshot del mes más reciente (datos actuales para el comparador)
# ---------------------------------------------------------------------------
print("\nGenerando snapshot del mes más reciente …")

latest_date = shs_plat_filtered["date"].max()
print(f"  Fecha más reciente disponible: {latest_date.strftime('%Y-%m')}")

shs_latest = shs_plat_filtered[shs_plat_filtered["date"] == latest_date].copy()
shs_latest.to_csv("shs_platform_latest.csv", index=False)
print(f"  Filas en snapshot: {len(shs_latest):,}")
print("  → Guardado: shs_platform_latest.csv")

# También para el dataset global
latest_global = shs_filtered["date"].max()
shs_global_latest = shs_filtered[shs_filtered["date"] == latest_global].copy()
shs_global_latest.to_csv("shs_latest.csv", index=False)
print(f"  → Guardado: shs_latest.csv ({len(shs_global_latest)} filas)")

print("\n✅ Filtrado completado.")
