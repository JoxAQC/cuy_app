import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Sistema Zootécnico", layout="wide")

st.title("📊 Sistema de Evaluación Zootécnica")
st.markdown("Sube tu archivo CSV con los siguientes campos:")
st.code("TRATAMIENTOS, REPETICIONES, Peso Inicial, Peso Final, Ganancia de peso, Conversión alimenticia, Rendimiento de Carcasa (%)")

# Carga
def cargar_datos(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()  # eliminar espacios en los encabezados

    required_cols = ["REPETICIONES", "Peso Inicial", "Peso Final", "Ganancia de peso", "Conversión alimenticia", "Rendimiento de Carcasa (%)"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"❌ Faltan columnas requeridas en tu archivo: {', '.join(missing)}")
        st.stop()

    df["Tratamiento"] = df["REPETICIONES"].astype(str).str.extract(r'([A-Z]+[0-9]*)')
    return df

# Resumen por tratamiento
def resumen_por_tratamiento(df):
    return df.groupby("Tratamiento")[[
        "Peso Inicial", "Peso Final", "Ganancia de peso",
        "Conversión alimenticia", "Rendimiento de Carcasa (%)"
    ]].mean().round(2).reset_index()

# Gráficos
def mostrar_graficos(df):
    st.subheader("📊 Gráficos comparativos")
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    sns.boxplot(data=df, x="Tratamiento", y="Ganancia de peso", ax=axs[0])
    sns.boxplot(data=df, x="Tratamiento", y="Conversión alimenticia", ax=axs[1])
    sns.boxplot(data=df, x="Tratamiento", y="Rendimiento de Carcasa (%)", ax=axs[2])
    axs[0].set_title("Ganancia de peso por Tratamiento")
    axs[1].set_title("Conversión alimenticia por Tratamiento")
    axs[2].set_title("Rendimiento de Carcasa por Tratamiento")
    st.pyplot(fig)

# UI principal
file = st.file_uploader("Selecciona el archivo (.csv, .xls, .xlsx)", type=["csv", "xls", "xlsx"])

if file:
    df = cargar_datos(file)
    st.subheader("📋 Datos procesados")
    st.dataframe(df)

    st.subheader("📌 Resumen por tratamiento")
    resumen = resumen_por_tratamiento(df)
    st.dataframe(resumen)

    mostrar_graficos(df)

    st.subheader("⬇ Exportar resultados")
    csv = resumen.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar resumen", csv, "resumen_zootecnico.csv", "text/csv")
