"""
etl/run_etl.py
==============
Orquestador del pipeline ETL completo.

Ejecuta en orden:
  1. clean_games.py      — limpia dataset de juegos (Kaggle)
  2. filter_steam_hw.py  — filtra Steam HW Survey (sin Mac, categorias relevantes)
  3. integrate.py        — cruza las 3 fuentes y produce dataset final

Uso:
  python etl/run_etl.py

El log completo se guarda en logs/etl.log
"""

import logging
import sys
import time
from pathlib import Path

# Agregar raiz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import etl.clean_games as clean_games
import etl.filter_steam_hw as filter_steam_hw
import etl.integrate as integrate

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
logger = logging.getLogger("run_etl")


def run_step(name: str, fn) -> bool:
    """Ejecuta un paso del pipeline y maneja errores."""
    logger.info(f"{'='*50}")
    logger.info(f"PASO: {name}")
    logger.info(f"{'='*50}")
    start = time.time()
    try:
        fn()
        elapsed = time.time() - start
        logger.info(f"  OK — {name} completado en {elapsed:.1f}s")
        return True
    except Exception as e:
        logger.error(f"  FALLO — {name}: {e}")
        return False


def main():
    logger.info("=" * 60)
    logger.info("INICIO PIPELINE ETL — EV3 Requerimientos de Hardware")
    logger.info("=" * 60)

    start_total = time.time()
    resultados = {}

    # Paso 1: Limpiar dataset de juegos
    resultados["clean_games"]     = run_step("Limpieza Kaggle (clean_games)",       clean_games.run)

    # Paso 2: Filtrar Steam HW Survey
    resultados["filter_steam_hw"] = run_step("Filtrado Steam HW (filter_steam_hw)", filter_steam_hw.run)

    # Paso 3: Integrar las 3 fuentes
    resultados["integrate"]       = run_step("Integracion de fuentes (integrate)",  integrate.run)

    # Resumen
    elapsed_total = time.time() - start_total
    logger.info("=" * 60)
    logger.info(f"RESUMEN PIPELINE ({elapsed_total:.1f}s total)")
    logger.info("=" * 60)
    all_ok = True
    for paso, ok in resultados.items():
        estado = "OK" if ok else "FALLO"
        logger.info(f"  {estado:6s} — {paso}")
        if not ok:
            all_ok = False

    if all_ok:
        logger.info("\nPipeline completado exitosamente.")
        logger.info("Outputs generados:")
        logger.info("  data/kaggle/games_clean.csv")
        logger.info("  data/steamhwsurvey/shs_platform_filtered.csv")
        logger.info("  data/steamhwsurvey/shs_platform_latest.csv")
        logger.info("  data/integrated/requirements_market.csv")
    else:
        logger.error("\nEl pipeline termino con errores. Revisa logs/etl.log")
        sys.exit(1)


if __name__ == "__main__":
    main()
