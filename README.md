# Retail Price Pipeline

Pipeline automatizado de datos de precios de consumo con predicciones — Fuente: INE España.

Live demo: https://retail-price-pipeline.streamlit.app/

## Qué hace

Pipeline ETL completo que descarga automáticamente datos del IPC de España desde la API oficial del INE, los limpia y transforma, los almacena en una base de datos SQLite, entrena un modelo de predicción y muestra todo en un dashboard interactivo actualizable en tiempo real.

## Funcionalidades

- Extracción automática de datos del IPC desde la API del INE
- Transformación — media móvil, IPC acumulado, clasificación de tendencia
- Almacenamiento en SQLite
- Modelo de regresión polinomial para predecir los próximos 12 meses
- Dashboard con evolución histórica, predicción y resumen anual
- Botón para actualizar datos y reentrenar el modelo en un clic

## Arquitectura
```
API INE → extract.py → transform.py → load.py → SQLite
                                                    ↓
                                              predict.py → modelo
                                                    ↓
                                               app.py → Streamlit
```

## Tecnologías

- Python 3.11
- pandas
- scikit-learn
- SQLite / SQLAlchemy
- Plotly
- Streamlit
- API pública del INE

## Cómo ejecutarlo
```bash
git clone https://github.com/JurgenSchuldt/retail-price-pipeline.git
cd retail-price-pipeline
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```


