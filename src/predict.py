import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os

MODEL_PATH = "models/price_model.pkl"

def train_model(df):
    print("Entrenando modelo de predicción...")
    
    df = df.sort_values("fecha").reset_index(drop=True)
    df["t"] = range(len(df))
    
    X = df[["t"]].values
    y = df["ipc_acumulado"].values
    
    # Modelo polinomial grado 2
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)
    
    model = LinearRegression()
    model.fit(X_poly, y)
    
    y_pred = model.predict(X_poly)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    
    print(f"MAE: {mae:.4f} | R²: {r2:.4f}")
    
    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "poly": poly, "n_train": len(df)}, f)
    
    print(f"Modelo guardado en {MODEL_PATH}")
    return model, poly, len(df)

def predict_future(n_months=12):
    if not os.path.exists(MODEL_PATH):
        print("No hay modelo entrenado.")
        return None
    
    with open(MODEL_PATH, "rb") as f:
        saved = pickle.load(f)
    
    model = saved["model"]
    poly = saved["poly"]
    n_train = saved["n_train"]
    
    future_t = np.array(range(n_train, n_train + n_months)).reshape(-1, 1)
    future_poly = poly.transform(future_t)
    predictions = model.predict(future_poly)
    
    return predictions

if __name__ == "__main__":
    from load import load_from_db
    df = load_from_db()
    train_model(df)
    preds = predict_future(12)
    print(f"\nPredicciones próximos 12 meses (IPC acumulado):")
    print(preds)

