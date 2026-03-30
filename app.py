import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.extract import get_ipc_data
from src.transform import transform_data
from src.load import save_to_db, load_from_db
from src.predict import train_model, predict_future

st.set_page_config(
    page_title="Retail Price Pipeline",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #f0f4f8; }
    .block-container { padding-top: 1.5rem; }
    .dashboard-header {
        background-color: #1e3a5f;
        padding: 16px 24px;
        border-radius: 8px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .dashboard-title { color: white; font-size: 20px; font-weight: 600; margin: 0; }
    .dashboard-sub { color: #8ab4d4; font-size: 13px; margin: 0; }
    .kpi-card {
        background: white;
        border-left: 4px solid #1e3a5f;
        border-radius: 6px;
        padding: 14px 18px;
    }
    .kpi-value { font-size: 24px; font-weight: 600; color: #1e3a5f; margin: 0; }
    .kpi-label { font-size: 12px; color: #888; margin: 0; }
    .section-title {
        font-size: 13px; font-weight: 600;
        color: #1e3a5f; margin-bottom: 8px;
        text-transform: uppercase; letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <div>
        <p class="dashboard-title">Retail Price Pipeline</p>
        <p class="dashboard-sub">Pipeline automatizado de precios de consumo — Fuente: INE España</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Pipeline ─────────────────────────────────────────────────────
col_btn, col_status = st.columns([1, 3])

with col_btn:
    if st.button("Actualizar datos", type="primary"):
        with st.spinner("Ejecutando pipeline..."):
            df_raw = get_ipc_data()
            df_clean = transform_data(df_raw)
            save_to_db(df_clean)
            train_model(df_clean)
            st.success("Pipeline ejecutado correctamente")
            st.rerun()

# ── Cargar datos ─────────────────────────────────────────────────
df = load_from_db()

if df is None or len(df) == 0:
    st.warning("No hay datos. Pulsa 'Actualizar datos' para ejecutar el pipeline.")
    st.stop()

# ── KPIs ─────────────────────────────────────────────────────────
ultimo_ipc = df["ipc"].iloc[-1]
ipc_acumulado = df["ipc_acumulado"].iloc[-1]
media_anual = df[df["año"] == df["año"].max()]["ipc"].mean()
tendencia_actual = df["tendencia"].iloc[-1]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-label">Último IPC mensual</p>
        <p class="kpi-value">{ultimo_ipc:.1f}%</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-label">IPC acumulado</p>
        <p class="kpi-value">{ipc_acumulado:.1f}%</p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-label">Media anual {df["año"].max()}</p>
        <p class="kpi-value">{media_anual:.2f}%</p>
    </div>""", unsafe_allow_html=True)

with col4:
    color = "#1D9E75" if tendencia_actual == "Estable" else ("#d32f2f" if tendencia_actual == "Subida" else "#378ADD")
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-label">Tendencia actual</p>
        <p class="kpi-value" style="color:{color}">{tendencia_actual}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Gráfico 1: Evolución IPC ─────────────────────────────────────
st.markdown('<p class="section-title">Evolución del IPC mensual</p>', unsafe_allow_html=True)

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=df["fecha"], y=df["ipc"],
    name="IPC mensual",
    marker_color=df["ipc"].apply(lambda x: "#d32f2f" if x > 0.3 else ("#378ADD" if x < -0.3 else "#888")),
))
fig1.add_trace(go.Scatter(
    x=df["fecha"], y=df["media_movil_3m"],
    name="Media móvil 3m",
    line=dict(color="#1e3a5f", width=2)
))
fig1.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(t=10, b=10, l=10, r=10),
    height=300, xaxis_title="", yaxis_title="IPC (%)"
)
st.plotly_chart(fig1, use_container_width=True)

# ── Gráfico 2: IPC acumulado + predicción ────────────────────────
st.markdown('<p class="section-title">IPC acumulado y predicción a 12 meses</p>', unsafe_allow_html=True)

preds = predict_future(12)

if preds is not None:
    last_date = df["fecha"].max()
    future_dates = [last_date + pd.DateOffset(months=i+1) for i in range(12)]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["fecha"], y=df["ipc_acumulado"],
        name="Histórico", line=dict(color="#1e3a5f", width=2)
    ))
    fig2.add_trace(go.Scatter(
        x=future_dates, y=preds,
        name="Predicción", line=dict(color="#d32f2f", width=2, dash="dash")
    ))
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=10, b=10, l=10, r=10),
        height=300, xaxis_title="", yaxis_title="IPC acumulado (%)"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Tabla resumen por año ────────────────────────────────────────
st.markdown('<p class="section-title">Resumen anual</p>', unsafe_allow_html=True)

resumen = df.groupby("año").agg(
    IPC_medio=("ipc", "mean"),
    IPC_max=("ipc", "max"),
    IPC_min=("ipc", "min"),
    Meses=("ipc", "count")
).round(2).reset_index()

st.dataframe(resumen, use_container_width=True, hide_index=True)

st.markdown('<p style="font-size:11px;color:#aaa;margin-top:16px">Fuente: INE España — Índice de Precios de Consumo</p>', unsafe_allow_html=True)

