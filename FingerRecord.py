import tkinter as tk
import serial
import csv
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk  # Importa la biblioteca Pillow
import os
from datetime import datetime

# Variables globales para el hilo de lectura y el estado de la lectura
lector_activo = False
nombre_archivo_csv = None

# Listas para almacenar los datos leídos
tiempos = []
datos = []
contador_muestras = 1


def obtener_hora_actual():
    ahora = time.strftime("%Y-%m-%d_%H-%M-%S")  # Formato: AAAA-MM-DD_HH-MM-SS
    return ahora


# Función para iniciar la lectura del puerto serial y guardar los datos en el archivo CSV
def reproducir():
    global lector_activo, nombre_archivo_csv
    nombre_dedo = entrada_nombre_dedo.get()
    if nombre_dedo:
        boton_play.config(state=tk.DISABLED)
        nombre_carpeta_records = "Records"
        nombre_carpeta_fecha = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(nombre_carpeta_records):
            os.makedirs(
                nombre_carpeta_records
            )  # Crear la carpeta "Records" si no existe
        if not os.path.exists(
            os.path.join(nombre_carpeta_records, nombre_carpeta_fecha)
        ):
            os.makedirs(
                os.path.join(nombre_carpeta_records, nombre_carpeta_fecha)
            )  # Crear carpeta con la fecha del día si no existe

        nombre_archivo_base = f"{nombre_dedo}.csv"
        ruta_carpeta = os.path.join(nombre_carpeta_records, nombre_carpeta_fecha)
        ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo_base)

        if os.path.exists(ruta_archivo):
            indice = 1
            # Buscar un nombre de archivo único con un índice
            while True:
                nombre_archivo_csv = os.path.join(
                    ruta_carpeta, f"{nombre_dedo}_{indice}.csv"
                )
                if not os.path.exists(nombre_archivo_csv):
                    break
                indice += 1
        else:
            nombre_archivo_csv = ruta_archivo
        etiqueta_estado.config(text=f"Leyendo datos de {nombre_dedo}...")
        lector_activo = True
        thread_lector = threading.Thread(target=leer_puerto_serial)
        thread_lector.start()
    else:
        etiqueta_estado.config(text="Ingrese nombre del archivo")


# Función para detener la lectura del puerto serial y guardar el archivo CSV
def detener():
    global lector_activo, nombre_archivo_csv
    if lector_activo:
        etiqueta_estado.config(text="Deteniendo y guardando datos...")
        lector_activo = False
        nombre_archivo_csv = None
        boton_play.config(state=tk.NORMAL)
    else:
        etiqueta_estado.config(text="La lectura ya está detenida")


# Función para la lectura del puerto serial en segundo plano
def leer_puerto_serial():
    global lector_activo, nombre_archivo_csv, contador_muestras
    with open(nombre_archivo_csv, mode="w", newline="") as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow(["Muestra", "Valor"])  # Cambiamos 'Tiempo' a 'Muestra'

        # Configura el puerto serial
        puerto_serial = serial.Serial(
            "COM7", 115200
        )  # Cambia 'COM1' al nombre de tu puerto serial y la velocidad (baudrate) según sea necesario

        def read_binary_data(serial_port, data_size):
            data = serial_port.read(data_size)  # Lee los datos binarios
            return int.from_bytes(
                data, byteorder="little"
            )  # Convierte los datos binarios a un entero

        while lector_activo:
            # linea_serial = puerto_serial.readline().decode("utf-8").strip()

            data_size = 2  # El tamaño de los datos binarios que esperas recibir
            linea_serial = read_binary_data(puerto_serial, data_size)
            muestra_actual = contador_muestras  # Obtiene el valor actual del contador
            contador_muestras += 1  # Incrementa el contador para la próxima muestra

            escritor_csv.writerow([muestra_actual, linea_serial])

            # Agrega los datos a las listas para trazarlos
            tiempos.append(muestra_actual)  # Usamos el contador como muestra
            datos.append(float(linea_serial))  # Supongo que los datos son números

            # Actualiza el gráfico
            actualizar_grafico()

        etiqueta_estado.config(text="Lectura detenida y datos guardados")


# Función para actualizar el gráfico
def actualizar_grafico():
    # Limpia el gráfico anterior y traza los nuevos datos
    ax.clear()
    ax.plot(tiempos, datos)
    ax.set_xlabel("Muestras")
    ax.set_ylabel("Señal EMG")
    ax.grid(True)

    canvas.draw()


def resetear_grafico():
    global tiempos, datos, contador_muestras
    tiempos = []
    datos = []
    contador_muestras = 1
    ax.clear()
    ax.set_xlabel("Muestras")
    ax.set_ylabel("Señal EMG")

    ax.grid(True)
    canvas.draw()

    entrada_nombre_dedo.delete(0, tk.END)


def llenar_dedo(dedo):
    entrada_nombre_dedo.delete(
        0, tk.END
    )  # Borra el contenido actual del campo de entrada
    entrada_nombre_dedo.insert(0, dedo)  # Inserta "Indice" en el campo de entrada


# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Record EMG Signal")
ventana.iconbitmap("Iconos/musculo.ico")

# Configurar el tamaño de la ventana (ancho x alto)
ventana.geometry("800x700")  # Aumenté el alto para dar espacio al gráfico


# Crear un frame para contener los elementos
frame_contenedor = tk.Frame(ventana, padx=20, pady=10)
frame_contenedor.pack()


# Campo de entrada (Input)
etiqueta_nombre_dedo = tk.Label(frame_contenedor, text="Nombre del archivo:")
etiqueta_nombre_dedo.pack()
entrada_nombre_dedo = tk.Entry(frame_contenedor)
entrada_nombre_dedo.pack(padx=10, pady=5)

frame_botones_dedos = tk.Frame(frame_contenedor, padx=20, pady=10)
frame_botones_dedos.pack()

frame_botones = tk.Frame(frame_contenedor, padx=20, pady=10)
frame_botones.pack()

# -----------------Botones de reproducción----------------------------------------------

# Botón de reproducción (play) con margen
imagen_play = Image.open(
    "Iconos/play.png"
)  # Reemplaza "play.png" con la ruta a tu imagen de botón Play
imagen_play = imagen_play.resize(
    (32, 32)
)  # Ajusta el tamaño de la imagen según sea necesario
imagen_play = ImageTk.PhotoImage(imagen_play)

imagen_stop = Image.open(
    "Iconos/stop.png"
)  # Reemplaza "stop.png" con la ruta a tu imagen de botón Stop
imagen_stop = imagen_stop.resize(
    (32, 32)
)  # Ajusta el tamaño de la imagen según sea necesario
imagen_stop = ImageTk.PhotoImage(imagen_stop)

imagen_reset = Image.open(
    "Iconos/reset.png"
)  # Reemplaza "reset.png" con la ruta a tu imagen de botón Reset
imagen_reset = imagen_reset.resize(
    (32, 32)
)  # Ajusta el tamaño de la imagen según sea necesario
imagen_reset = ImageTk.PhotoImage(imagen_reset)

# Botón de reproducción (play) con imagen personalizada
boton_play = tk.Button(frame_botones, image=imagen_play, command=reproducir)
boton_play.pack(side=tk.LEFT, padx=5)

# Botón de detención (stop) con imagen personalizada
boton_stop = tk.Button(frame_botones, image=imagen_stop, command=detener)
boton_stop.pack(side=tk.LEFT, padx=5)

# Botón de reset para limpiar el gráfico y el campo de entrada con imagen personalizada
boton_reset = tk.Button(frame_botones, image=imagen_reset, command=resetear_grafico)
boton_reset.pack(side=tk.LEFT, padx=5)

# --------------------------Botones para cada dedo----------------------------------------------
dedo_pulgar = Image.open("Iconos/pulgar.png")
dedo_pulgar = dedo_pulgar.resize((62, 62))
dedo_pulgar = ImageTk.PhotoImage(dedo_pulgar)

boton_pulgar = tk.Button(
    frame_botones_dedos, image=dedo_pulgar, command=lambda: llenar_dedo("Pulgar")
)
boton_pulgar.pack(side=tk.LEFT, padx=5)

dedo_indice = Image.open(
    "Iconos/indice.png"
)  # Reemplaza "Indice.png" con la ruta a tu imagen de botón Indice
dedo_indice = dedo_indice.resize((62, 62))
dedo_indice = ImageTk.PhotoImage(dedo_indice)

boton_indice = tk.Button(
    frame_botones_dedos, image=dedo_indice, command=lambda: llenar_dedo("Indice")
)
boton_indice.pack(side=tk.LEFT, padx=5)

dedo_medio = Image.open(
    "Iconos/medio.png"
)  # Reemplaza "Indice.png" con la ruta a tu imagen de botón Indice
dedo_medio = dedo_medio.resize((62, 62))
dedo_medio = ImageTk.PhotoImage(dedo_medio)

boton_medio = tk.Button(
    frame_botones_dedos, image=dedo_medio, command=lambda: llenar_dedo("Medio")
)
boton_medio.pack(side=tk.LEFT, padx=5)

dedo_anular = Image.open(
    "Iconos/Anular.png"
)  # Reemplaza "Indice.png" con la ruta a tu imagen de botón Indice
dedo_anular = dedo_anular.resize((62, 62))
dedo_anular = ImageTk.PhotoImage(dedo_anular)

boton_anular = tk.Button(
    frame_botones_dedos, image=dedo_anular, command=lambda: llenar_dedo("Anular")
)
boton_anular.pack(side=tk.LEFT, padx=5)

dedo_meñique = Image.open(
    "Iconos/Meñique.png"
)  # Reemplaza "Indice.png" con la ruta a tu imagen de botón Indice
dedo_meñique = dedo_meñique.resize((62, 62))
dedo_meñique = ImageTk.PhotoImage(dedo_meñique)

boton_meñique = tk.Button(
    frame_botones_dedos, image=dedo_meñique, command=lambda: llenar_dedo("Meñique")
)
boton_meñique.pack(side=tk.LEFT, padx=5)

punio = Image.open(
    "Iconos/Punio.png"
)  # Reemplaza "Indice.png" con la ruta a tu imagen de botón Indice
punio = punio.resize((62, 62))
punio = ImageTk.PhotoImage(punio)

boton_punio = tk.Button(
    frame_botones_dedos, image=punio, command=lambda: llenar_dedo("Puño")
)
boton_punio.pack(side=tk.LEFT, padx=5)

flexionPunio = Image.open("Iconos/Punioflexionada.png")
flexionPunio = flexionPunio.resize((62, 62))
flexionPunio = ImageTk.PhotoImage(flexionPunio)

boton_flexionPunio = tk.Button(
    frame_botones_dedos,
    image=flexionPunio,
    command=lambda: llenar_dedo("Puño Flexionado"),
)
boton_flexionPunio.pack(side=tk.LEFT, padx=5)


# --------------------------------Etiqueta de estado-----------------------------------------------
etiqueta_estado = tk.Label(frame_contenedor, text="", fg="blue")
etiqueta_estado.pack()

# ----------------------------Configurar el gráfico de matplotlib------------------------------------
fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=frame_contenedor)
canvas.get_tk_widget().pack()
ax.set_xlabel("Muestras")
ax.set_ylabel("Señal EMG")
ax.grid(True)

# ---------------------------------- Iniciar la aplicación------------------------------------
ventana.mainloop()
