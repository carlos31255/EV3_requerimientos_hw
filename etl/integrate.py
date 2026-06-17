"""
etl/integrate.py
================
Integra las tres fuentes de datos del pipeline EV3:

  1. games_clean.csv          — requisitos de cada juego (Kaggle)
  2. shs_platform_latest.csv  — hardware real de jugadores (Steam HW Survey)
  3. [stub]                   — precios de componentes (eBay via API)

Produce data/integrated/requirements_market.csv con:
  - Requisitos del juego (cpu, ram, gpu, storage, os)
  - Cuota de mercado Steam para cada nivel de RAM y GPU del juego
  - gpu_tier        : clasificacion por nivel (legacy/low/mid/high/ultra)
  - gpu_match_status: indica si la GPU matcheo con Steam (found/legacy/unknown)
  - Columnas de precio vacias (stubs que la rama 'api' llenara en tiempo real)

La logica de mercado:
  - RAM : dado el requisito "8 GB", calcula el % acumulado de usuarios
          con >= 8 GB segun la Steam HW Survey
  - GPU : busca coincidencia por nombre del modelo en el ranking de GPUs.
          Si no hay match, clasifica por tier usando patrones de modelo para
          que la API pueda buscar un equivalente moderno en eBay.

Salida: data/integrated/requirements_market.csv
"""

import logging
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from etl.schemas import GAMES_SCHEMA, STEAM_SCHEMA, PARTPICKER_SCHEMA
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
logger = logging.getLogger("integrate")

# ─────────────────────────────────────────────
# Rutas
# ─────────────────────────────────────────────
GAMES_PATH  = Path("data/kaggle/games_clean.csv")
STEAM_PATH  = Path("data/steamhwsurvey/shs_platform_latest.csv")
OUT_DIR     = Path("data/integrated")
OUT_PATH    = OUT_DIR / "requirements_market.csv"

# ─────────────────────────────────────────────
# Helpers de parseo
# ─────────────────────────────────────────────
_RAM_ORDER = {
    "128 MB": 0.128, "256 MB": 0.256, "512 MB": 0.512,
    "1 GB": 1, "2 GB": 2, "3 GB": 3, "4 GB": 4,
    "6 GB": 6, "8 GB": 8, "12 GB": 12, "16 GB": 16,
    "24 GB": 24, "32 GB": 32, "64 GB": 64,
}

def parse_ram_gb(value: str) -> float | None:
    """Extrae el valor numerico en GB de un string de RAM (ej. '8 GB' -> 8.0)."""
    if not isinstance(value, str):
        return None
    value = value.strip().upper()
    match_gb = re.search(r"([\d.]+)\s*GB", value)
    match_mb = re.search(r"([\d.]+)\s*MB", value)
    if match_gb:
        return float(match_gb.group(1))
    if match_mb:
        return float(match_mb.group(1)) / 1024
    return None


def build_ram_market_table(steam_df: pd.DataFrame) -> dict[float, float]:
    """
    Construye tabla {ram_gb: pct_players_with_at_least_that_ram}.
    Usa la categoria 'System RAM' de la Steam HW Survey.
    """
    ram_df = steam_df[
        (steam_df["platform"] == "pc") &
        (steam_df["category"].str.contains("System RAM", case=False, na=False))
    ].copy()

    if ram_df.empty:
        logger.warning("No se encontraron datos de System RAM en Steam HW Survey")
        return {}

    ram_df["ram_gb"] = ram_df["name"].apply(parse_ram_gb)
    ram_df = ram_df.dropna(subset=["ram_gb"]).sort_values("ram_gb")

    # % acumulado de usuarios con >= X GB (de mayor a menor)
    total_pct = ram_df["percentage"].sum()
    cumulative: dict[float, float] = {}
    running = 0.0
    for _, row in ram_df.sort_values("ram_gb", ascending=False).iterrows():
        running += row["percentage"]
        cumulative[row["ram_gb"]] = min(running / total_pct, 1.0)

    return cumulative


def lookup_ram_market(req_gb: float | None, ram_table: dict) -> float | None:
    """Devuelve el % de jugadores con >= req_gb de RAM."""
    if req_gb is None or not ram_table:
        return None
    # Encuentra el nivel de RAM mas cercano por debajo o igual
    candidates = sorted([k for k in ram_table if k <= req_gb], reverse=True)
    if candidates:
        return round(ram_table[candidates[0]], 4)
    # Si el requisito es menor que todos los niveles, casi todos lo cumplen
    return 1.0


def build_gpu_market_table(steam_df: pd.DataFrame) -> pd.Series:
    """Extrae el % de mercado por modelo de GPU desde Steam HW Survey."""
    gpu_df = steam_df[
        (steam_df["platform"] == "pc") &
        (steam_df["category"].str.contains("Video Card Description", case=False, na=False))
    ].copy()
    gpu_df["name_lower"] = gpu_df["name"].str.lower().str.strip()
    return gpu_df.set_index("name_lower")["percentage"]


def lookup_gpu_market(gpu_name: str | None, gpu_table: pd.Series) -> float | None:
    """Busca el % de mercado de un modelo de GPU por nombre (busqueda parcial)."""
    if not isinstance(gpu_name, str) or gpu_table.empty:
        return None
    gpu_lower = gpu_name.lower().strip()
    # Coincidencia exacta
    if gpu_lower in gpu_table.index:
        return round(gpu_table[gpu_lower], 4)
    # Busqueda parcial: busca el modelo con mas overlap
    matches = gpu_table[gpu_table.index.str.contains(gpu_lower, na=False, regex=False)]
    if not matches.empty:
        return round(matches.iloc[0], 4)
    return None


# Patrones para clasificacion por tier (se evaluan en orden, primer match gana)
# Formato: (regex_pattern, tier)
_GPU_TIER_RULES: list[tuple[str, str]] = [
    # NVIDIA — Ultra
    (r"rtx\s*(40[6-9]\d|50\d\d)", "ultra"),
    (r"rtx\s*30[89]\d", "ultra"),
    # NVIDIA — High
    (r"rtx\s*30[5-7]\d", "high"),
    (r"rtx\s*20[6-9]\d", "high"),
    (r"gtx\s*1080", "high"),
    (r"gtx\s*1070", "high"),
    # NVIDIA — Mid
    (r"rtx\s*30[0-4]\d", "mid"),
    (r"rtx\s*20[0-5]\d", "mid"),
    (r"gtx\s*1060", "mid"),
    (r"gtx\s*9[5-9]\d", "mid"),
    (r"gtx\s*780", "mid"),
    (r"gtx\s*770", "mid"),
    (r"gtx\s*680", "mid"),
    (r"gtx\s*670", "mid"),
    # NVIDIA — Low
    (r"gtx\s*1050", "low"),
    (r"gtx\s*9[0-4]\d", "low"),
    (r"gtx\s*7[0-6]\d", "low"),
    (r"gtx\s*6[0-6]\d", "low"),
    (r"geforce\s*gtx\s*[5-9]\d\d", "low"),
    # NVIDIA — Legacy (modelos antiguos sin numero o muy bajos)
    (r"geforce\s*(2\d\d|3\d\d|4\d\d|5\d\d|6\d\d|7\d\d|8\d\d|9\d\d)\b", "legacy"),
    (r"geforce\s*[4-9]\d{3}", "legacy"),
    (r"quadro", "legacy"),
    # AMD/ATI — Ultra
    (r"rx\s*79\d\d", "ultra"),
    (r"rx\s*68[0-9]\d", "ultra"),
    (r"rx\s*69\d\d", "ultra"),
    # AMD — High
    (r"rx\s*67\d\d", "high"),
    (r"rx\s*66\d\d", "high"),
    (r"rx\s*57[0-9]\d", "high"),
    (r"radeon\s*vii", "high"),
    # AMD — Mid
    (r"rx\s*65\d\d", "mid"),
    (r"rx\s*5[56]\d\d", "mid"),
    (r"rx\s*5[89]\d", "mid"),
    (r"r9\s*29\d", "mid"),
    (r"r9\s*39\d", "mid"),
    # AMD — Low
    (r"rx\s*5[57]\d", "low"),
    (r"rx\s*4[0-9]\d", "low"),
    (r"r9\s*2[7-8]\d", "low"),
    (r"r9\s*3[7-8]\d", "low"),
    (r"r7\s*2[0-9]\d", "low"),
    # AMD/ATI — Legacy
    (r"(ati|amd)\s*(radeon\s*)?hd\s*[1-6]\d{3}", "legacy"),
    (r"(ati|amd)\s*(radeon\s*)?hd\s*7\d{3}", "low"),
    (r"(ati|firemv|firegl|firestream)", "legacy"),
    # Intel — Integrated (categoria propia, no comparable con discreta)
    (r"intel\s*(hd|uhd|iris\s*plus|iris\s*xe?)", "integrated"),
    (r"intel\s*(media\s*accelerator|gma)", "legacy"),
    (r"intel\s*arc", "mid"),
]


def classify_gpu_tier(gpu_name: str | None) -> str:
    """
    Clasifica una GPU en un tier de rendimiento basado en el nombre del modelo.

    Tiers:
      ultra     — gama alta actual (RTX 4080+, RX 7900+)
      high      — gama alta accesible (RTX 3060-3070, RX 6600-6700)
      mid       — gama media (GTX 1060, RX 580, RTX 2060)
      low       — gama baja / entrada (GTX 1050, RX 550-570)
      integrated— GPU integrada (Intel HD, Intel UHD, Iris)
      legacy    — GPU obsoleta sin datos en Steam HW Survey actual
      unknown   — no se pudo clasificar
    """
    if not isinstance(gpu_name, str):
        return "unknown"
    name = gpu_name.lower().strip()
    for pattern, tier in _GPU_TIER_RULES:
        if re.search(pattern, name):
            return tier
    return "unknown"


def get_gpu_match_status(
    gpu_name: str | None,
    gpu_table: pd.Series,
    market_pct: float | None,
) -> str:
    """
    Devuelve el estado del matching de GPU:
      found    — matcheo con Steam HW Survey (tiene market_pct)
      legacy   — GPU muy antigua, no aparece en Steam Survey actual
      unknown  — GPU no reconocida ni por Steam ni por el clasificador
    """
    if pd.notna(market_pct):
        return "found"
    tier = classify_gpu_tier(gpu_name)
    if tier == "legacy":
        return "legacy"
    return "unknown"


# ─────────────────────────────────────────────
# Pipeline principal
# ─────────────────────────────────────────────

def run() -> pd.DataFrame:
    """Integra las 3 fuentes y genera requirements_market.csv."""
    logger.info("=== Inicio: integrate.py ===")

    try:
        # ── Fuente 1: juegos limpios (Kaggle) ─────────────────────
        if not GAMES_PATH.exists():
            raise FileNotFoundError(f"Ejecuta clean_games.py primero: {GAMES_PATH}")
        logger.info(f"Cargando juegos: {GAMES_PATH}")
        games = pd.read_csv(GAMES_PATH)
        games, _ = validate_dataframe(games, GAMES_SCHEMA, logger)
        logger.info(f"  {len(games):,} juegos cargados")

        # ── Fuente 2: Steam HW Survey (snapshot reciente) ──────────
        if not STEAM_PATH.exists():
            raise FileNotFoundError(f"Ejecuta filter_steam_hw.py primero: {STEAM_PATH}")
        logger.info(f"Cargando Steam HW Survey: {STEAM_PATH}")
        steam = pd.read_csv(STEAM_PATH, parse_dates=["date"])
        steam, _ = validate_dataframe(steam, STEAM_SCHEMA, logger)
        logger.info(f"  {len(steam):,} registros Steam cargados")

        # ── Fuente 3: PCPartPicker (stub — la rama api lo llenara) ──
        logger.info("Fuente 3 (PCPartPicker): columnas stub reservadas para la rama 'api'")
        stub_columns = {
            "price_cpu_usd":     pd.NA,
            "price_ram_usd":     pd.NA,
            "price_gpu_usd":     pd.NA,
            "price_storage_usd": pd.NA,
            "total_upgrade_usd": pd.NA,
        }

        # ── Tablas de mercado ──────────────────────────────────────
        logger.info("Construyendo tablas de mercado...")
        ram_table = build_ram_market_table(steam)
        gpu_table = build_gpu_market_table(steam)
        logger.info(f"  RAM: {len(ram_table)} niveles | GPU: {len(gpu_table)} modelos")

        # ── Cruce ──────────────────────────────────────────────────
        logger.info("Cruzando requisitos con datos de mercado...")
        games["ram_gb_req"]     = games["ram"].apply(parse_ram_gb)
        games["ram_market_pct"] = games["ram_gb_req"].apply(
            lambda x: lookup_ram_market(x, ram_table)
        )
        games["gpu_market_pct"] = games["gpu"].apply(
            lambda x: lookup_gpu_market(x, gpu_table)
        )

        # Clasificacion de GPU por tier y estado de match
        logger.info("Clasificando GPUs por tier de rendimiento...")
        games["gpu_tier"] = games["gpu"].apply(classify_gpu_tier)
        games["gpu_match_status"] = [
            get_gpu_match_status(gpu, gpu_table, pct)
            for gpu, pct in zip(games["gpu"], games["gpu_market_pct"])
        ]

        # Agregar stubs de precios (columnas vacias para la API)
        for col, val in stub_columns.items():
            games[col] = val

        # Columna de fecha de la encuesta usada
        games["steam_survey_date"] = steam["date"].max().strftime("%Y-%m")

        # ── Guardar ────────────────────────────────────────────────
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        games.to_csv(OUT_PATH, index=False, encoding="utf-8")
        logger.info(f"  Guardado: {OUT_PATH} ({len(games):,} filas)")

        # Reporte de cobertura
        ram_covered = games["ram_market_pct"].notna().sum()
        gpu_covered = games["gpu_market_pct"].notna().sum()
        logger.info(
            f"  Cobertura RAM  : {ram_covered:,}/{len(games):,} juegos"
        )
        logger.info(
            f"  Cobertura GPU  : {gpu_covered:,}/{len(games):,} juegos (match Steam)"
        )
        # Reporte de tiers
        tier_counts = games["gpu_tier"].value_counts()
        match_counts = games["gpu_match_status"].value_counts()
        logger.info(f"  GPU Tiers      : {tier_counts.to_dict()}")
        logger.info(f"  GPU Match      : {match_counts.to_dict()}")

    except FileNotFoundError as e:
        logger.error(str(e))
        raise
    except ValueError as e:
        logger.error(f"Error de validacion: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado en integrate: {e}", exc_info=True)
        raise

    logger.info("=== Fin: integrate.py ===\n")
    return games


if __name__ == "__main__":
    run()
