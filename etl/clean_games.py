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
  6. Validar esquema del resultado con validate.py

Entrada : data/kaggle/PC_video_games_requirements.csv
Salida  : data/kaggle/games_clean.csv
"""

import logging
import sys
from pathlib import Path

import pandas as pd

# Agregar raiz del proyecto al path para importar modulos etl
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from etl.schemas import GAMES_SCHEMA
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
logger = logging.getLogger("clean_games")

# ─────────────────────────────────────────────
# Rutas
# ─────────────────────────────────────────────
INPUT  = Path("data/kaggle/PC_video_games_requirements.csv")
OUTPUT = Path("data/kaggle/games_clean.csv")


def load_raw(path: Path) -> pd.DataFrame:
    """Carga el CSV raw con validacion de existencia."""
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    logger.info(f"Cargando: {path}")
    df = pd.read_csv(path)
    logger.info(f"  {len(df):,} filas | {len(df.columns)} columnas")
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renombra columnas a snake_case estandar."""
    mapping = {
        "name"           : "game_name",
        "Memory:"        : "ram",
        "Graphics Card:" : "gpu",
        "CPU:"           : "cpu",
        "File Size:"     : "storage",
        "OS:"            : "os",
    }
    df = df.rename(columns=mapping)
    logger.info(f"  Columnas renombradas: {list(mapping.values())}")
    return df


def strip_strings(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Elimina espacios en blanco sobrantes en columnas de texto."""
    for col in cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    logger.info("  Strip de espacios aplicado")
    return df


def clean_game_name(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina el sufijo ' System Requirements' del nombre del juego."""
    before = df["game_name"].iloc[0] if len(df) > 0 else ""
    df["game_name"] = (
        df["game_name"]
        .str.replace(r"\s*System Requirements\s*$", "", regex=True)
        .str.strip()
    )
    after = df["game_name"].iloc[0] if len(df) > 0 else ""
    logger.info(f"  Nombre limpiado: '{before}' -> '{after}'")
    return df


def normalize_unknown(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Reemplaza variantes de 'Unknown' y 'nan' por NaN."""
    pattern = r"(?i)^(unknown|nan)$"
    for col in cols:
        if col in df.columns:
            df[col] = df[col].replace(to_replace=pattern, value=pd.NA, regex=True)
    logger.info("  Valores 'Unknown'/'nan' normalizados a NaN")
    return df


def drop_empty_hardware_rows(df: pd.DataFrame, hw_cols: list) -> pd.DataFrame:
    """Elimina filas donde todos los campos de hardware son nulos."""
    before = len(df)
    df = df.dropna(subset=hw_cols, how="all")
    dropped = before - len(df)
    logger.info(f"  Filas eliminadas (todo nulo): {dropped:,}")
    return df


def run(input_path: Path = INPUT, output_path: Path = OUTPUT) -> pd.DataFrame:
    """Ejecuta el pipeline completo de limpieza."""
    logger.info("=== Inicio: clean_games.py ===")

    try:
        # 1. Carga
        df = load_raw(input_path)

        # 2. Renombrar columnas
        df = rename_columns(df)

        # 3. Strip de espacios
        str_cols = ["game_name", "ram", "gpu", "cpu", "storage", "os"]
        df = strip_strings(df, str_cols)

        # 4. Limpiar nombre del juego
        df = clean_game_name(df)

        # 5. Normalizar Unknown
        hw_cols = ["ram", "gpu", "cpu", "storage", "os"]
        df = normalize_unknown(df, hw_cols)

        # 6. Eliminar filas con todos los campos de hardware nulos
        df = drop_empty_hardware_rows(df, hw_cols)

        # 7. Reordenar columnas
        df = df[["game_name", "cpu", "ram", "gpu", "storage", "os"]]

        # 8. Validar esquema
        df, report = validate_dataframe(df, GAMES_SCHEMA, logger)

        # 9. Guardar
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding="utf-8")
        logger.info(f"  Guardado en: {output_path} ({len(df):,} filas)")

    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        raise
    except ValueError as e:
        logger.error(f"Error de validacion: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado en clean_games: {e}", exc_info=True)
        raise

    logger.info("=== Fin: clean_games.py ===\n")
    return df


if __name__ == "__main__":
    run()
