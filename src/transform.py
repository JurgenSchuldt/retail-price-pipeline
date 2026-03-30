import pandas as pd
import numpy as np

def transform_data(df):
    print("Transformando datos...")
    
    df = df.copy()
    df = df.sort_values("fecha").reset_index(drop=True)
    
    # IPC acumulado (suma acumulada de variaciones mensuales)
    df["ipc_acumulado"] = df["ipc"].cumsum()
    
    # Media móvil 3 y 6 meses
    df["media_movil_3m"] = df["ipc"].rolling(window=3).mean()
    df["media_movil_6m"] = df["ipc"].rolling(window=6).mean()
    
    # Tendencia — positiva, negativa o estable
    df["tendencia"] = df["ipc"].apply(
        lambda x: "Subida" if x > 0.3 else ("Bajada" if x < -0.3 else "Estable")
    )
    
    # Año y mes
    df["año"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["mes_nombre"] = df["fecha"].dt.strftime("%b %Y")
    
    print(f"Transformación completada: {len(df)} registros")
    print(df[["fecha", "ipc", "ipc_acumulado", "media_movil_3m", "tendencia"]].tail(5))
    
    return df

if __name__ == "__main__":
    from extract import get_ipc_data
    df = get_ipc_data()
    df_clean = transform_data(df)
