import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Sistema Zootécnico", layout="wide")

st.title("📊 Sistema de Evaluación Zootécnica")
st.markdown("Sube tu archivo CSV o Excel con los siguientes campos:")
st.code("TRATAMIENTOS, REPETICIONES, Peso Inicial, Peso Final, Ganancia de peso, Consumo de alimento, Conversión alimenticia, Rendimiento de Carcasa (%)")

# Carga de datos
def cargar_datos(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()  # eliminar espacios en los encabezados
    
    # 1. Eliminar columnas que estén completamente vacías (solo tienen None o NaN)
    #    Esto lo hacemos primero para simplificar el DataFrame inicial.
    df = df.dropna(axis=1, how='all')

    required_cols = [
        "REPETICIONES", "Peso Inicial", "Peso Final", "Ganancia de peso",
        "Consumo de alimento", "Conversión alimenticia", "Rendimiento de Carcasa (%)"
    ]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"❌ ¡Ups! Faltan columnas requeridas en tu archivo: {', '.join(missing)}. Por favor, asegúrate de incluirlas todas.")
        st.stop()

    # Extraer "Tratamiento" ANTES de la limpieza de filas
    df["Tratamiento"] = df["REPETICIONES"].astype(str).str.extract(r'([A-Z]+\d+)')
    
    if "TRATAMIENTOS" in df.columns:
        df["Tratamiento"] = df["TRATAMIENTOS"].astype(str)
        
    # --- CAMBIO AQUÍ: Limpieza de datos (ahora al final) ---
    # 2. Ahora sí, eliminar filas con valores NaN.
    #    Filtramos el DataFrame para que solo contenga los valores no nulos
    #    en las columnas que realmente nos interesan para el análisis.
    #    Así evitamos borrar filas enteras por celdas vacías en otras columnas.
    df_clean = df.dropna(subset=required_cols + ["Tratamiento"]).reset_index(drop=True)
    
    initial_rows = df.shape[0]
    final_rows = df_clean.shape[0]
    
    if initial_rows > final_rows:
        st.warning(f"⚠️ Se han eliminado {initial_rows - final_rows} filas con datos faltantes en las columnas de análisis.")
    
    return df_clean

# Resumen por tratamiento
def resumen_por_tratamiento(df):
    return df.groupby("Tratamiento")[[
        "Peso Inicial", "Peso Final", "Ganancia de peso",
        "Consumo de alimento", "Conversión alimenticia", "Rendimiento de Carcasa (%)"
    ]].mean().round(2).reset_index()

# Gráficos
def mostrar_graficos(df):
    st.subheader("📊 Gráficos comparativos")
    
    fig, axs = plt.subplots(1, 4, figsize=(24, 5))
    
    sns.boxplot(data=df, x="Tratamiento", y="Ganancia de peso", ax=axs[0])
    sns.boxplot(data=df, x="Tratamiento", y="Consumo de alimento", ax=axs[1])
    sns.boxplot(data=df, x="Tratamiento", y="Conversión alimenticia", ax=axs[2])
    sns.boxplot(data=df, x="Tratamiento", y="Rendimiento de Carcasa (%)", ax=axs[3])
    
    axs[0].set_title("Ganancia de peso por Tratamiento")
    axs[1].set_title("Consumo de alimento por Tratamiento")
    axs[2].set_title("Conversión alimenticia por Tratamiento")
    axs[3].set_title("Rendimiento de Carcasa por Tratamiento")
    
    plt.tight_layout()
    st.pyplot(fig)

# Interfaz de usuario principal
file = st.file_uploader("Selecciona el archivo (.csv, .xls, .xlsx)", type=["csv", "xls", "xlsx"])

if file:
    try:
        df = cargar_datos(file)
        
        if df.empty:
            st.warning("⚠️ El archivo subido está vacío o no contiene datos válidos después de la limpieza. Asegúrate de que las filas no estén vacías en las columnas de análisis.")
        else:
            st.subheader("📋 Datos procesados")
            st.dataframe(df)
        
            st.subheader("📌 Resumen por tratamiento")
            resumen = resumen_por_tratamiento(df)
            st.dataframe(resumen)

            mostrar_graficos(df)

            st.subheader("⬇ Exportar resultados")
            csv = resumen.to_csv(index=False).encode("utf-8")
            st.download_button("Descargar resumen", csv, "resumen_zootecnico.csv", "text/csv")
            
    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar el archivo: {e}. Asegúrate de que el formato sea correcto.")
