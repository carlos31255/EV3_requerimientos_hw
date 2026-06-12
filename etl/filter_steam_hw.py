"""
etl/filter_steam_hw.py
======================
Pipeline ETL para la Steam Hardware Survey.

Filtra shs_platform.csv para:
  - Eliminar datos de Mac (plataforma 'mac')
  - Conservar solo Windows ('pc') y Linux ('linux')
  - Quedarse con categorias de hardware relevantes para comparar
    requisitos de juegos (GPU, CPU, RAM, almacenamiento, SO)

Genera cuatro archivos en data/steamhwsurvey/:
  - shs_platform_filtered.csv : historico completo pc+linux filtrado
  - shs_filtered.csv          : datos globales filtrados por categoria
  - shs_platform_latest.csv   : snapshot del mes mas reciente (pc+linux)
  - shs_latest.csv            : snapshot del mes mas reciente (global)

Fuente raw: data/steamhwsurvey/shs_platform.csv
"""

import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from etl.schemas import STEAM_SCHEMA
from etl.validate import validate_dataframe

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "etl.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("filter_steam_hw")

# ─────────────────────────────────────────────
# Rutas
# ─────────────────────────────────────────────
DATA_DIR   = Path("data/steamhwsurvey")
INPUT_PLAT = DATA_DIR / "shs_platform.csv"
INPUT_SHS  = Path("steamHWsurvey/shs.csv")   # upstream de jdegene si existe

# ─────────────────────────────────────────────
# Categorias relevantes
# ─────────────────────────────────────────────
RELEVANT_KEYWORDS = [
    "Video Card Description",
    "VRAM",
    "DirectX 12 GPUs",
    "DirectX 11 GPUs",
    "Vulkan",
    "Physical CPUs",
    "Processor Vendor",
    "Intel CPU Speeds",
    "AMD CPU Speeds",
    "System RAM",
    "Drive Type",
    "Free Hard Drive Space",
    "Total Hard Drive Space",
    "Primary Display Resolution",
    "Windows Version",
    "Linux Version",
    "OS Version",
]

def is_relevant(category: str) -> bool:
    cat_lower = category.lower()
    return any(kw.lower() in cat_lower for kw in RELEVANT_KEYWORDS)


def load_platform_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    logger.info(f"Cargando: {path}")
    df = pd.read_csv(path, parse_dates=["date"])
    logger.info(f"  {len(df):,} filas | Plataformas: {df['platform'].value_counts().to_dict()}")
    return df


def filter_platforms(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina Mac, conserva pc y linux."""
    df_filtered = df[df["platform"].isin(["pc", "linux"])].copy()
    removed = len(df) - len(df_filtered)
    logger.info(f"  Mac eliminada: {removed:,} filas removidas")
    return df_filtered


def filter_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Conserva solo las categorias de hardware relevantes."""
    df_filtered = df[df["category"].apply(is_relevant)].copy()
    logger.info(f"  Categorias relevantes: {len(df_filtered):,} filas conservadas")
    return df_filtered


def get_latest_snapshot(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Extrae el snapshot del mes mas reciente."""
    latest = df["date"].max()
    df_latest = df[df["date"] == latest].copy()
    label = latest.strftime("%Y-%m")
    logger.info(f"  Snapshot {label}: {len(df_latest):,} filas")
    return df_latest, label


def run() -> dict:
    """Ejecuta el pipeline completo de filtrado."""
    logger.info("=== Inicio: filter_steam_hw.py ===")
    outputs = {}

    try:
        # ── 1. shs_platform.csv (por plataforma) ──────────────────
        df_plat = load_platform_csv(INPUT_PLAT)

        df_no_mac = filter_platforms(df_plat)
        df_filtered = filter_categories(df_no_mac)

        # Validar esquema
        df_filtered, _ = validate_dataframe(df_filtered, STEAM_SCHEMA, logger)

        # Guardar historico filtrado
        out = DATA_DIR / "shs_platform_filtered.csv"
        df_filtered.to_csv(out, index=False)
        logger.info(f"  Guardado: {out}")
        outputs["shs_platform_filtered"] = df_filtered

        # Snapshot mas reciente
        df_latest, label = get_latest_snapshot(df_filtered)
        out_latest = DATA_DIR / "shs_platform_latest.csv"
        df_latest.to_csv(out_latest, index=False)
        logger.info(f"  Guardado: {out_latest} (snapshot {label})")
        outputs["shs_platform_latest"] = df_latest

        # ── 2. shs.csv global (si existe) ─────────────────────────
        if INPUT_SHS.exists():
            logger.info(f"Cargando datos globales: {INPUT_SHS}")
            df_glob = pd.read_csv(INPUT_SHS, parse_dates=["date"])
            df_glob_filtered = df_glob[df_glob["category"].apply(is_relevant)].copy()

            out_glob = DATA_DIR / "shs_filtered.csv"
            df_glob_filtered.to_csv(out_glob, index=False)
            logger.info(f"  Guardado: {out_glob} ({len(df_glob_filtered):,} filas)")
            outputs["shs_filtered"] = df_glob_filtered

            df_glob_latest, label_glob = get_latest_snapshot(df_glob_filtered)
            out_glob_latest = DATA_DIR / "shs_latest.csv"
            df_glob_latest.to_csv(out_glob_latest, index=False)
            logger.info(f"  Guardado: {out_glob_latest} (snapshot {label_glob})")
            outputs["shs_latest"] = df_glob_latest
        else:
            logger.warning(f"shs.csv no encontrado en {INPUT_SHS}, omitiendo datos globales.")

    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        raise
    except ValueError as e:
        logger.error(f"Error de validacion: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado en filter_steam_hw: {e}", exc_info=True)
        raise

    logger.info("=== Fin: filter_steam_hw.py ===\n")
    return outputs


if __name__ == "__main__":
    run()
