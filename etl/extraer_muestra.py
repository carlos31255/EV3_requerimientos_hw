import pandas as pd
import os
import logging

# Configuración de logging profesional
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/etl.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("etl")

# Archivos de entrada
kaggle_file = "data/kaggle/PC_video_games_requirements.csv"
steam_file = "steamHWsurvey/shs.csv"  # El raw global (ignorado por .gitignore)

# Archivos de salida (muestras)
kaggle_out = "data/kaggle/games_sample_15.csv"
steam_out  = "data/steamhwsurvey/steam_sample_15.csv"


def extract_kaggle_sample():
    """Extrae una muestra de 15 juegos populares del dataset de Kaggle."""
    logger.info("Iniciando extracción de muestra Kaggle...")

    if not os.path.exists(kaggle_file):
        logger.error(f"Archivo no encontrado: {kaggle_file}")
        return

    df = pd.read_csv(kaggle_file)
    logger.info(f"Dataset cargado: {len(df)} filas.")

    # Limpiamos el nombre para facilitar la búsqueda
    df['name_clean'] = df['name'].astype(str).str.replace(r"\s*System Requirements\s*$", "", regex=True)

    juegos_populares = [
        "Cyberpunk 2077", "Grand Theft Auto V", "Valorant", "Fortnite",
        "Hogwarts Legacy", "Red Dead Redemption 2", "Minecraft", "League of Legends",
        "Elden Ring", "Call of Duty: Warzone", "The Witcher 3: Wild Hunt",
        "Apex Legends", "Counter-Strike: Global Offensive", "Overwatch 2", "Baldur's Gate 3"
    ]

    pattern = '|'.join(juegos_populares)
    sample_df = df[df['name_clean'].str.contains(pattern, case=False, na=False)].copy()
    sample_df = sample_df.drop_duplicates(subset=['name_clean']).head(15)
    sample_df = sample_df.drop(columns=['name_clean'])

    sample_df.to_csv(kaggle_out, index=False)
    logger.info(f"Muestra guardada en '{kaggle_out}' ({len(sample_df)} juegos).")


def extract_steam_sample():
    """Extrae top GPUs, RAMs y almacenamiento de la Steam Hardware Survey."""
    logger.info("Iniciando extracción de muestra Steam HW Survey...")

    if not os.path.exists(steam_file):
        logger.warning(f"Archivo principal no encontrado: {steam_file}. Buscando alternativa...")
        steam_file_alt = "data/steamhwsurvey/shs_platform.csv"
        if not os.path.exists(steam_file_alt):
            logger.error("No hay datos raw de Steam disponibles. Abortando.")
            return
        df = pd.read_csv(steam_file_alt)
        logger.info(f"Usando alternativa: {steam_file_alt}")
    else:
        df = pd.read_csv(steam_file)

    logger.info(f"Dataset cargado: {len(df)} filas.")

    if 'platform' in df.columns:
        df = df[df['platform'] == 'pc']
        logger.info(f"Filtrado por plataforma 'pc': {len(df)} filas.")

    latest_date = df['date'].max()
    df_latest = df[df['date'] == latest_date]
    logger.info(f"Datos del período más reciente: {latest_date} ({len(df_latest)} filas).")

    gpus    = df_latest[df_latest['category'].str.contains('Video Card Description', na=False, case=False)]
    gpus    = gpus.sort_values('percentage', ascending=False).head(10)
    rams    = df_latest[df_latest['category'].str.contains('System RAM', na=False, case=False)]
    rams    = rams.sort_values('percentage', ascending=False).head(5)
    storage = df_latest[df_latest['category'].str.contains('Total Hard Drive Space', na=False, case=False)]
    storage = storage.sort_values('percentage', ascending=False).head(5)

    sample_df = pd.concat([gpus, rams, storage])
    sample_df.to_csv(steam_out, index=False)
    logger.info(f"Muestra guardada en '{steam_out}' ({len(sample_df)} filas).")


if __name__ == "__main__":
    logger.info("=== ETL iniciado ===")
    extract_kaggle_sample()
    extract_steam_sample()
    logger.info("=== ETL finalizado ===")
