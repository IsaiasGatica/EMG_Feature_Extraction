import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import pandas as pd
import plotly.io as pio

import pywt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def cargar_datos_desde_archivos(archivos):
    data_frames = []
    for archivo in archivos:
        # Leer el archivo CSV y almacenar los datos en un DataFrame, omitiendo la primera fila
        df = pd.read_csv(archivo, skiprows=1, names=["Muestras", "Valores"])

        # Extraer el nombre del dedo de la ruta del archivo
        dedo_nombre = archivo.split("/")[1].split(".")[0]

        # Agregar el nombre del dedo como una columna
        df["Dedo"] = dedo_nombre

        data_frames.append(df)

    # Concatenar todos los DataFrames en uno solo
    data = pd.concat(data_frames, ignore_index=True)

    return data


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------


def obtener_muestras(dataframe, dedo, rangos):
    muestras_rango = []

    for i, rango in enumerate(rangos):
        submuestra = dataframe[
            (dataframe["Muestras"] >= rango[0])
            & (dataframe["Muestras"] <= rango[1])
            & (dataframe["Dedo"] == dedo)
        ]["Valores"].tolist()

        muestras_rango.append(submuestra)

    longitud_maxima = max(len(submuestra) for submuestra in muestras_rango)

    # Rellenar submuestras más cortas con ceros
    muestras_rango = [
        submuestra + [0] * (longitud_maxima - len(submuestra))
        for submuestra in muestras_rango
    ]

    return muestras_rango


# -------------------------------------------------------------Gráficos---------------------------------------------------------------------------------------------


def graficar_df(valores_graficar):
    fig = px.line(
        valores_graficar,
        template="plotly_dark",
        x="Muestras",
        y="Valores",
        color="Dedo",
        title="Gráfico de Varios Dedos",
    )

    fig.show()
    # pio.write_html(fig, "nombre_del_archivo.html")


def grafico_comp2(senal_graficar0, senal_graficar1):
    fig = px.line(template="plotly_dark")
    fig.add_scatter(y=senal_graficar0, mode="lines")
    fig.add_scatter(y=senal_graficar1, mode="lines")
    fig.show()


def graficar_coeficientes_subplot(coefs):
    fig = make_subplots(
        rows=len(coefs),
        cols=1,
        subplot_titles=[f"Coeficiente {i+1}" for i in range(len(coefs))],
    )

    for i, coef in enumerate(coefs, start=1):
        fig.add_trace(
            go.Scatter(y=coef, mode="lines", name="Anular Coef" + str(i)), row=i, col=1
        )
        fig.update_xaxes(title_text="Muestras", row=i, col=1)
        fig.update_yaxes(title_text="Coeficiente", row=i, col=1)

    fig.update_layout(
        height=1200, width=1600, title_text="Coeficientes", template="plotly_dark"
    )
    fig.show()


def graficar_listas(*senal_lists, names=None, titulo=""):
    fig = go.Figure()

    if names is None:
        names = ["Lista"] * len(senal_lists)

    for senal_list, nombre in zip(senal_lists, names):
        # Agregar los valores de la lista al gráfico
        fig.add_trace(
            go.Scatter(
                x=list(range(len(senal_list))),
                y=senal_list,
                mode="lines",
                name=nombre,
            )
        )

    fig.update_xaxes(title_text="Muestras")
    fig.update_yaxes(title_text="Valor")
    fig.update_layout(title=titulo, template="plotly_dark")
    fig.show()


def graficar_coeficientes(coefs0, coefs1, coefs2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=coefs0, mode="lines"))
    fig.add_trace(go.Scatter(y=coefs1, mode="lines"))
    fig.add_trace(go.Scatter(y=coefs2, mode="lines"))
    fig.update_xaxes(title_text="Muestras")
    fig.update_yaxes(title_text="Coeficiente")

    fig.update_layout(
        height=600, width=1600, title_text="Coeficientes", template="plotly_dark"
    )
    fig.show()


# ---------------------------------------------Wavelet----------------------------------------------------------------------------------------


def transformadaWavelet(muestras, wavelet, nivel_descomposicion):
    coefs = pywt.wavedec(muestras, wavelet, level=nivel_descomposicion)
    return coefs


def reconstruccionWavelet(coefs, wavelet):
    coefs_reconstruccion = coefs[:3] + [None] * 1

    senal_reconstruida = pywt.waverec(coefs_reconstruccion, wavelet)
    return senal_reconstruida


# --------------------------------------------Características----------------------------------------------------------------------------------------------


def calcular_MAV(datos):
    mav = sum(abs(x) for x in datos) / len(datos)
    return mav


def calcular_STD(datos):
    std = np.std(datos)
    return std


def calcular_RMS(datos):
    rms = np.sqrt(np.mean(np.square(datos)))
    return rms


def calcular_VAR(datos):
    var = np.var(datos)
    return var


def calcular_WL(datos):
    differences = np.diff(datos)
    wl = np.sum(np.abs(differences))
    return wl


def calcular_DMAV(datos):
    dmav = np.abs(datos - np.mean(datos))
    dmav = np.mean(dmav)
    return dmav


def calcular_SSI(datos):
    ssi = np.sum(np.abs(datos) ** 2)
    return ssi


def calcular_SSC(datos):
    # Calcular la derivada de la señal
    derivative = np.diff(datos)

    # Contar los cambios de signo en la derivada
    ssc = np.sum(np.diff(np.sign(derivative)) != 0)

    return ssc


def calcular_Entropy(datos):
    # Asegurarse de que no haya ceros en los datos
    datos_no_cero = datos - np.min(datos) + 1e-10  # Ajustar y agregar un valor pequeño

    # Calcular la entropía
    entropia = -np.sum(
        (datos_no_cero / np.sum(datos_no_cero))
        * np.log2(datos_no_cero / np.sum(datos_no_cero))
    )

    return entropia


def calcular_Mean_Derivative(datos):
    derivative = np.diff(datos)
    mean_derivative = np.mean(derivative)
    return mean_derivative


def calcular_caracteristica_lista(listas, funcion_calculo):
    return [[funcion_calculo(valores) for valores in sublist] for sublist in listas]
