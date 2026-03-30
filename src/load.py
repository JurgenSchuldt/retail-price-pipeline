import pandas as pd
import sqlalchemy as sa
import os

DB_PATH = "data/retail_prices.db"

def get_engine():
    return sa.create_engine(f"sqlite:///{DB_PATH}")

def save_to_db(df):
    print("Guardando datos en base de datos...")
    engine = get_engine()
    df.to_sql("ipc_data", engine, if_exists="replace", index=False)
    print(f"Guardados {len(df)} registros en {DB_PATH}")

def load_from_db():
    engine = get_engine()
    if not os.path.exists(DB_PATH):
        return None
    df = pd.read_sql("SELECT * FROM ipc_data", engine)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df

if __name__ == "__main__":
    from extract import get_ipc_data
    from transform import transform_data
    df = get_ipc_data()
    df_clean = transform_data(df)
    save_to_db(df_clean)
    df_loaded = load_from_db()
    print(f"\nDatos cargados desde DB: {len(df_loaded)} registros")
    print(df_loaded.tail(3))

