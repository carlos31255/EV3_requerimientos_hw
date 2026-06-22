import pandas as pd
import os

# Archivos de entrada
kaggle_file = "data/kaggle/PC_video_games_requirements.csv"
steam_file = "steamHWsurvey/shs.csv" # El raw global

# Archivos de salida (muestras)
kaggle_out = "data/kaggle/games_sample_15.csv"
steam_out = "data/steamhwsurvey/steam_sample_15.csv"

def extract_kaggle_sample():
    print("Extrayendo 15 juegos populares de Kaggle...")
    df = pd.read_csv(kaggle_file)
    
    # Limpiamos un poco el nombre para que sea mas facil buscar
    df['name_clean'] = df['name'].astype(str).str.replace(r"\s*System Requirements\s*$", "", regex=True)
    
    # Seleccionamos 15 juegos muy conocidos manualmente para que la presentacion al profe sea coherente
    juegos_populares = [
        "Cyberpunk 2077", "Grand Theft Auto V", "Valorant", "Fortnite", 
        "Hogwarts Legacy", "Red Dead Redemption 2", "Minecraft", "League of Legends",
        "Elden Ring", "Call of Duty: Warzone", "The Witcher 3: Wild Hunt",
        "Apex Legends", "Counter-Strike: Global Offensive", "Overwatch 2", "Baldur's Gate 3"
    ]
    
    # Filtramos los juegos que coincidan (insensible a mayusculas)
    pattern = '|'.join(juegos_populares)
    sample_df = df[df['name_clean'].str.contains(pattern, case=False, na=False)].copy()
    
    # Nos quedamos con exactamente 15 (eliminando duplicados si hay)
    sample_df = sample_df.drop_duplicates(subset=['name_clean']).head(15)
    
    # Quitamos la columna auxiliar
    sample_df = sample_df.drop(columns=['name_clean'])
    
    sample_df.to_csv(kaggle_out, index=False)
    print(f"✅ Creado: {kaggle_out} ({len(sample_df)} filas)")


def extract_steam_sample():
    print("\nExtrayendo 15 datos de Steam Hardware Survey...")
    if not os.path.exists(steam_file):
        print(f"No se encontro {steam_file}. Buscando en raw platforms...")
        steam_file_alt = "data/steamhwsurvey/shs_platform.csv"
        if not os.path.exists(steam_file_alt):
            print("No hay datos raw de steam para extraer.")
            return
        df = pd.read_csv(steam_file_alt)
    else:
        df = pd.read_csv(steam_file)
        
    # Filtramos para PC y categorias relevantes, tomamos el mes mas reciente (mayo 2026 segun vimos antes)
    if 'platform' in df.columns:
        df = df[df['platform'] == 'pc']
        
    latest_date = df['date'].max()
    df_latest = df[df['date'] == latest_date]
    
    # Sacamos el top 10 de GPUs y el top 5 de RAM
    gpus = df_latest[df_latest['category'].str.contains('Video Card Description', na=False, case=False)]
    gpus = gpus.sort_values('percentage', ascending=False).head(10)
    
    rams = df_latest[df_latest['category'].str.contains('System RAM', na=False, case=False)]
    rams = rams.sort_values('percentage', ascending=False).head(5)
    
    sample_df = pd.concat([gpus, rams])
    
    sample_df.to_csv(steam_out, index=False)
    print(f"✅ Creado: {steam_out} ({len(sample_df)} filas)")

if __name__ == "__main__":
    extract_kaggle_sample()
    extract_steam_sample()
