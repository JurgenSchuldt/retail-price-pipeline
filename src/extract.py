import requests
import pandas as pd
from datetime import datetime

def get_ipc_data():
    url = "https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/IPC206449?nult=60"
    
    print("Descargando datos del IPC desde el INE...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    
    records = []
    for item in data["Data"]:
        fecha = datetime.fromtimestamp(item["Fecha"] / 1000)
        valor = item["Valor"]
        if valor is not None:
            records.append({
                "fecha": fecha.strftime("%Y-%m-%d"),
                "ipc": float(valor)
            })
    
    df = pd.DataFrame(records)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha").reset_index(drop=True)
    
    print(f"Datos descargados: {len(df)} registros")
    print(f"Periodo: {df['fecha'].min()} → {df['fecha'].max()}")
    
    return df

if __name__ == "__main__":
    df = get_ipc_data()
    print(df.tail(10))