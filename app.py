import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Sistema Zootécnico", layout="wide")

st.title("📊 Sistema de Evaluación Zootécnica")
st.markdown("Sube tu archivo CSV con los siguientes campos:")
st.code("ID, Semana, Peso Inicial, Peso Final, Consumo, Peso Carcasa [, Insumo]")

# Carga y procesamiento
def cargar_datos(file):
    df = pd.read_csv(file)
    df["Ganancia de Peso"] = df["Peso Final"] - df["Peso Inicial"]
    df["Conversión Alimenticia"] = df["Consumo"] / df["Ganancia de Peso"]
    df["Rendimiento de Carcasa (%)"] = (df["Peso Carcasa"] / df["Peso Final"]) * 100
    return df

def resumen_semanal(df):
    return df.groupby("Semana")[["Peso Final", "Ganancia de Peso", "Consumo", 
                                 "Conversión Alimenticia", "Rendimiento de Carcasa (%)"]].mean().reset_index()

def resumen_total(df):
    return df[["Peso Final", "Ganancia de Peso", "Consumo", 
               "Conversión Alimenticia", "Rendimiento de Carcasa (%)"]].mean()

def proyeccion(df):
    semanas = df["Semana"].values.reshape(-1, 1)
    ganancia = df["Ganancia de Peso"].values.reshape(-1, 1)
    modelo = LinearRegression().fit(semanas, ganancia)
    proyecciones = modelo.predict(semanas)
    return semanas.flatten(), ganancia.flatten(), proyecciones.flatten()

def comparar_insumos(df):
    if "Insumo" not in df.columns:
        st.warning("No se encontró una columna 'Insumo' para evaluar insumos alimenticios.")
        return
    st.subheader("📌 Comparación por Insumo")
    promedio_insumos = df.groupby("Insumo")[["Ganancia de Peso", "Conversión Alimenticia", "Rendimiento de Carcasa (%)"]].mean()
    st.dataframe(promedio_insumos.style.format("{:.2f}"))
    st.bar_chart(promedio_insumos)

def mostrar_graficos(df):
    st.subheader("📊 Gráficos Detallados")
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    sns.boxplot(data=df, x="Semana", y="Ganancia de Peso", ax=axs[0])
    sns.boxplot(data=df, x="Semana", y="Conversión Alimenticia", ax=axs[1])
    sns.boxplot(data=df, x="Semana", y="Rendimiento de Carcasa (%)", ax=axs[2])
    axs[0].set_title("Ganancia de Peso por Semana")
    axs[1].set_title("Conversión Alimenticia por Semana")
    axs[2].set_title("Rendimiento de Carcasa por Semana")
    st.pyplot(fig)

# UI
file = st.file_uploader("Selecciona el archivo .csv", type=["csv"])

if file:
    df = cargar_datos(file)
    st.subheader("📋 Datos procesados")
    st.dataframe(df)

    st.subheader("📆 Resumen semanal")
    st.dataframe(resumen_semanal(df))

    st.subheader("📊 Promedios totales")
    st.json(resumen_total(df).round(2).to_dict())

    mostrar_graficos(df)

    st.subheader("🔮 Proyección de Ganancia de Peso")
    semanas, ganancia, proyecciones = proyeccion(df)
    fig2, ax2 = plt.subplots()
    ax2.plot(semanas, ganancia, "o", label="Observado")
    ax2.plot(semanas, proyecciones, "-", label="Proyección")
    ax2.set_xlabel("Semana")
    ax2.set_ylabel("Ganancia de Peso")
    ax2.legend()
    st.pyplot(fig2)

    comparar_insumos(df)

    st.subheader("⬇ Exportar resultados")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", csv, "datos_procesados.csv", "text/csv")
