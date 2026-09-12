"""
TP 1 - Manipulación de luminancia y saturación

Objetivos:
- Convertir una imagen del espacio RGB al espacio YIQ.
- Modificar la luminancia mediante el coeficiente a.
- Modificar la saturación mediante el coeficiente b.
- Controlar los rangos de los componentes Y, I y Q.
- Convertir la imagen procesada nuevamente al espacio RGB.
- Visualizar, guardar y reutilizar la imagen resultado.

La interfaz utiliza como base la desarrollada en el TP 0.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image, ImageTk

# ============================================================
# FUNCIONES DE PDI - TP1
# ============================================================

# Matriz de transformación RGB -> YIQ
RGB_A_YIQ = np.array([
    [0.299,     0.587,      0.114],
    [0.595716, -0.274453,  -0.321263],
    [0.211456, -0.522591,   0.311135]
])

# Matriz de transformación YIQ -> RGB
YIQ_A_RGB = np.array([
    [1.0,  0.9663,  0.6210],
    [1.0, -0.2721, -0.6474],
    [1.0, -1.1070,  1.7046]
])

def rgb_a_yiq(imagen):
    """
    Convierte una imagen RGB normalizada al espacio YIQ.
    """
    # Aplicamos la transformación matricial a cada píxel RGB.
    return imagen @ RGB_A_YIQ.T


def yiq_a_rgb(imagen):
    """
    Convierte una imagen YIQ nuevamente al espacio RGB.
    """

    resultado = imagen @ YIQ_A_RGB.T
    return np.clip(
        resultado,
        0,
        1
    )


def modificar_luminancia_saturacion(imagen, a, b):
    """
    Modifica independientemente la luminancia y la saturación.
    a: coeficiente de luminancia.
    b: coeficiente de saturación.
    """

    # Convertimos RGB -> YIQ
    yiq = rgb_a_yiq(
        imagen
    )

    # Y representa la luminancia.
    yiq[:, :, 0] = (
        yiq[:, :, 0] * a
    )

    # I y Q representan la crominancia.
    # Modificamos ambos con el mismo coeficiente de saturación.
    yiq[:, :, 1] = (
        yiq[:, :, 1] * b
    )

    yiq[:, :, 2] = (
        yiq[:, :, 2] * b
    )

    # Controlamos los rangos indicados para YIQ.
    yiq[:, :, 0] = np.clip(
        yiq[:, :, 0],
        0,
        1
    )

    yiq[:, :, 1] = np.clip(
        yiq[:, :, 1],
        -0.5957,
        0.5957
    )

    yiq[:, :, 2] = np.clip(
        yiq[:, :, 2],
        -0.5226,
        0.5226
    )

    # Convertimos YIQ -> RGB.
    resultado = yiq_a_rgb(
        yiq
    )

    return resultado


def escala_grises(imagen):
    """
    Convierte una imagen RGB a escala de grises.

    La imagen llega como array:
        alto x ancho x 3

    El promedio de los tres canales genera un único valor
    de intensidad.

    Después repetimos ese canal 3 veces para conservar
    el formato RGB.
    """

    gris = imagen.mean(axis=2)

    resultado = np.stack(
        [gris, gris, gris],
        axis=2
    )

    return resultado


def solo_canal(imagen, canal):
    """
    Conserva solamente un canal RGB.

    canal:
        0 -> R
        1 -> G
        2 -> B
    """

    resultado = np.zeros_like(imagen)

    resultado[:, :, canal] = imagen[:, :, canal]

    return resultado


class AppPDI:

    def __init__(self, ventana):

        self.ventana = ventana
        self.ventana.title("PDI - Tkinter + NumPy")

        self.ventana.geometry("1100x650")

        # ----------------------------------------------------
        # Imágenes de la aplicación.
        #
        # imagen_original:
        #     Copia de la imagen cargada. No se modifica.
        #
        # imagen_entrada:
        #     Imagen que se encuentra a la izquierda.
        #     Es la entrada de los futuros procesamientos.
        #
        # imagen_procesada:
        #     Imagen que se encuentra a la derecha.
        #     Es el resultado de los futuros procesamientos.
        # ----------------------------------------------------

        self.imagen_original = None
        self.imagen_entrada = None
        self.imagen_procesada = None

        self.crear_interfaz()


    def crear_interfaz(self):

        barra = tk.Frame(self.ventana)

        barra.pack(
            side="top",
            fill="x",
            padx=10,
            pady=10
        )

        boton_abrir = tk.Button(
            barra,
            text="Abrir imagen",
            command=self.abrir_imagen
        )

        boton_abrir.pack(
            side="left",
            padx=5
        )

        boton_restaurar = tk.Button(
            barra,
            text="Restaurar original",
            command=self.restaurar_original
        )

        boton_restaurar.pack(
            side="left",
            padx=5
        )

        boton_guardar = tk.Button(
            barra,
            text="Guardar resultado",
            command=self.guardar_resultado
        )

        boton_guardar.pack(
            side="left",
            padx=5
        )

        # ----------------------------------------------------
        # Panel central
        # ----------------------------------------------------

        panel = tk.Frame(
            self.ventana
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # ----------------------------------------------------
        # Zona de imágenes
        # ----------------------------------------------------

        zona_imagenes = tk.Frame(
            panel
        )

        zona_imagenes.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # Imagen de entrada
        # ----------------------------------------------------

        frame_entrada = tk.Frame(
            zona_imagenes
        )

        frame_entrada.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        titulo_entrada = tk.Label(
            frame_entrada,
            text="ENTRADA",
            font=("Arial", 11, "bold")
        )

        titulo_entrada.pack(
            pady=5
        )

        self.label_entrada = tk.Label(
            frame_entrada,
            text="Abrí una imagen para comenzar",
            bg="#dddddd"
        )

        self.label_entrada.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # Imagen resultado
        # ----------------------------------------------------

        frame_resultado = tk.Frame(
            zona_imagenes
        )

        frame_resultado.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        titulo_resultado = tk.Label(
            frame_resultado,
            text="RESULTADO",
            font=("Arial", 11, "bold")
        )

        titulo_resultado.pack(
            pady=5
        )

        self.label_resultado = tk.Label(
            frame_resultado,
            text="El resultado aparecerá aquí",
            bg="#dddddd"
        )

        self.label_resultado.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # Panel de controles
        # ----------------------------------------------------

        controles = tk.Frame(panel)

        controles.pack(
            side="right",
            fill="y",
            padx=10
        )

        titulo_controles = tk.Label(
            controles,
            text="Controles",
            font=("Arial", 14, "bold")
        )

        titulo_controles.pack(
            pady=10
        )

        # ----------------------------------------------------
        # Pasar resultado a entrada
        # ----------------------------------------------------

        boton_pasar = tk.Button(
            controles,
            text="Usar resultado\ncomo entrada",
            command=self.pasar_resultado_a_entrada
        )

        boton_pasar.pack(
            fill="x",
            pady=10
        )

        # ----------------------------------------------------
        # Opciones de procesamiento
        # ----------------------------------------------------

        self.operacion = tk.StringVar()

        self.operacion.set(
            "Sin procesamiento"
        )

        opciones = [
            "Sin procesamiento",
            "Escala de grises",
            "Solo canal R",
            "Solo canal G",
            "Solo canal B"
        ]

        menu = tk.OptionMenu(
            controles,
            self.operacion,
            *opciones
        )

        menu.pack(
            fill="x",
            pady=5
        )

        # ----------------------------------------------------
        # Luminancia y saturación
        # ----------------------------------------------------

        tk.Label(
            controles,
            text="Luminancia (a):"
        ).pack(
            pady=(20, 5)
        )

        self.coeficiente_a = tk.StringVar()
        # a = 1 no modifica la luminancia.
        self.coeficiente_a.set("1.0")

        entrada_a = tk.Entry(
            controles,
            textvariable=self.coeficiente_a
        )

        entrada_a.pack(
            fill="x",
            pady=5
        )


        tk.Label(
            controles,
            text="Saturación (b):"
        ).pack(
            pady=(10, 5)
        )

        self.coeficiente_b = tk.StringVar()
        # b = 1 no modifica la saturación.
        self.coeficiente_b.set("1.0")

        entrada_b = tk.Entry(
            controles,
            textvariable=self.coeficiente_b
        )

        entrada_b.pack(
            fill="x",
            pady=5
        )


        boton_yiq = tk.Button(
            controles,
            text="Aplicar luminancia y saturación",
            command=self.aplicar_yiq
        )

        boton_yiq.pack(
            fill="x",
            pady=10
        )

        # ----------------------------------------------------
        # Botón aplicar
        # ----------------------------------------------------

        boton_aplicar = tk.Button(
            controles,
            text="Aplicar operación",
            command=self.aplicar_operacion
        )

        boton_aplicar.pack(
            fill="x",
            pady=10
        )

        # ----------------------------------------------------
        # Histograma
        # ----------------------------------------------------

        titulo_histograma = tk.Label(
            controles,
            text="Histograma de:"
        )

        titulo_histograma.pack(
            pady=(20, 5)
        )

        self.histograma_de = tk.StringVar()

        self.histograma_de.set(
            "Entrada"
        )

        menu_histograma = tk.OptionMenu(
            controles,
            self.histograma_de,
            "Entrada",
            "Resultado"
        )

        menu_histograma.pack(
            fill="x",
            pady=5
        )

        boton_histograma = tk.Button(
            controles,
            text="Mostrar histograma",
            command=self.mostrar_histograma
        )

        boton_histograma.pack(
            fill="x",
            pady=10
        )

        # ----------------------------------------------------
        # Estado
        # ----------------------------------------------------

        self.estado = tk.Label(
            self.ventana,
            text="Listo.",
            anchor="w"
        )

        self.estado.pack(
            side="bottom",
            fill="x",
            padx=10,
            pady=10
        )

    # ========================================================
    # ABRIR IMAGEN
    # ========================================================

    def abrir_imagen(self):

        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")
            ]
        )

        if not ruta:
            return

        # Pillow abre la imagen.
        imagen_pil = Image.open(
            ruta
        ).convert("RGB")

        # Convertimos Pillow -> NumPy.
        #
        # /255.0 normaliza:
        #
        # 0   -> 0.0
        # 255 -> 1.0
        #
        self.imagen_original = (
            np.array(imagen_pil) / 255.0
        )

        # Al comenzar, las tres imágenes son iguales.
        #
        # La original queda guardada sin modificaciones.
        self.imagen_entrada = (
            self.imagen_original.copy()
        )

        self.imagen_procesada = (
            self.imagen_original.copy()
        )

        # Mostramos la misma imagen en ambos espacios.
        self.mostrar_imagen(
            self.imagen_entrada,
            self.label_entrada
        )

        self.mostrar_imagen(
            self.imagen_procesada,
            self.label_resultado
        )

        self.estado.config(
            text="Imagen cargada correctamente."
        )

    # ========================================================
    # APLICAR LUMINANCIA Y SATURACIÓN
    # ========================================================

    def aplicar_yiq(self):

        if self.imagen_entrada is None:
            messagebox.showwarning(
                "Atención",
                "Primero abrí una imagen."
            )
            return

        try:
            a = float(
                self.coeficiente_a.get()
            )
            b = float(
                self.coeficiente_b.get()
            )
        except ValueError:
            messagebox.showwarning(
                "Atención",
                "Los coeficientes a y b deben ser números."
            )
            return

        # Aplicamos los coeficientes sobre la imagen de entrada.
        self.imagen_procesada = (
            modificar_luminancia_saturacion(
                self.imagen_entrada,
                a,
                b
            )
        )

        self.mostrar_imagen(
            self.imagen_procesada,
            self.label_resultado
        )

        self.estado.config(
            text=f"Luminancia a={a} - Saturación b={b}"
        )

    # ========================================================
    # APLICAR OPERACIÓN
    # ========================================================

    def aplicar_operacion(self):

        # Verificamos que exista una imagen.
        if self.imagen_entrada is None:

            messagebox.showwarning(
                "Atención",
                "Primero abrí una imagen."
            )

            return

        # Obtenemos la opción seleccionada.
        operacion = self.operacion.get()

        imagen = self.imagen_entrada

        # ----------------------------------------------------
        # Acá empieza la conexión entre Tkinter y PDI.
        # ----------------------------------------------------

        if operacion == "Sin procesamiento":

            resultado = imagen.copy()

        elif operacion == "Escala de grises":

            resultado = escala_grises(
                imagen
            )

        elif operacion == "Solo canal R":

            resultado = solo_canal(
                imagen,
                0
            )

        elif operacion == "Solo canal G":

            resultado = solo_canal(
                imagen,
                1
            )

        elif operacion == "Solo canal B":

            resultado = solo_canal(
                imagen,
                2
            )

        # Guardamos el resultado.
        self.imagen_procesada = resultado

        # Mostramos el resultado.
        self.mostrar_imagen(
            self.imagen_procesada,
            self.label_resultado
        )

        self.estado.config(
            text=f"Operación aplicada: {operacion}"
        )

    # ========================================================
    # MOSTRAR IMAGEN
    # ========================================================

    def mostrar_imagen(self, array_imagen, label):

        # Convertimos 0-1 nuevamente a 0-255.
        imagen_uint8 = (
            np.clip(
                array_imagen,
                0,
                1
            ) * 255
        ).astype(np.uint8)

        # NumPy -> Pillow
        imagen_pil = Image.fromarray(
            imagen_uint8
        )

        # Reducimos el tamaño solamente para visualizarla.
        #
        # El array original no cambia de tamaño.
        imagen_pil.thumbnail(
            (430, 500)
        )

        # Pillow -> Tkinter
        foto = ImageTk.PhotoImage(
            imagen_pil
        )

        # Guardamos la referencia en el Label para evitar
        # que Python elimine la imagen de memoria.
        label.foto = foto

        # Mostramos la imagen.
        label.config(
            image=foto,
            text=""
        )

    # ========================================================
    # PASAR RESULTADO A ENTRADA
    # ========================================================

    def pasar_resultado_a_entrada(self):

        if self.imagen_procesada is None:

            messagebox.showwarning(
                "Atención",
                "Primero abrí una imagen."
            )

            return

        # La imagen resultado pasa a ser la nueva entrada
        self.imagen_entrada = (
            self.imagen_procesada.copy()
        )

        self.mostrar_imagen(
            self.imagen_entrada,
            self.label_entrada
        )

        self.estado.config(
            text="La imagen resultado pasó a la entrada."
        )

    # ========================================================
    # RESTAURAR ORIGINAL
    # ========================================================

    def restaurar_original(self):

        if self.imagen_original is None:
            return

        # Recuperamos la copia original en el espacio de entrada.
        self.imagen_entrada = (
            self.imagen_original.copy()
        )

        self.mostrar_imagen(
            self.imagen_entrada,
            self.label_entrada
        )

        self.estado.config(
            text="Imagen original restaurada en la entrada."
        )

    # ========================================================
    # GUARDAR RESULTADO
    # ========================================================

    def guardar_resultado(self):

        if self.imagen_procesada is None:

            messagebox.showwarning(
                "Atención",
                "Primero abrí una imagen."
            )

            return

        ruta = filedialog.asksaveasfilename(
            title="Guardar imagen procesada",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png")
            ]
        )

        if not ruta:
            return

        # Convertimos nuevamente de 0-1 a uint8.
        imagen_uint8 = (
            np.clip(
                self.imagen_procesada,
                0,
                1
            ) * 255
        ).astype(np.uint8)

        # NumPy -> Pillow y guardamos.
        imagen_pil = Image.fromarray(
            imagen_uint8
        )

        imagen_pil.save(
            ruta
        )

        self.estado.config(
            text="Imagen resultado guardada correctamente."
        )

    # ========================================================
    # HISTOGRAMA
    # ========================================================

    def mostrar_histograma(self):

        if self.imagen_entrada is None:
            messagebox.showwarning(
                "Atención",
                "Primero abrí una imagen."
            )
            return

        if self.histograma_de.get() == "Entrada":
            imagen = self.imagen_entrada
            nombre = "Entrada"
        else:
            imagen = self.imagen_procesada
            nombre = "Resultado"

        gris = imagen.mean(
            axis=2
        )

        intensidades = (
            gris * 255
        ).astype(np.uint8)

        plt.hist(
            intensidades.reshape(-1),
            bins=32,
            color="gray"
        )

        plt.title(
            f"Histograma - Imagen {nombre}"
        )

        plt.xlabel(
            "Valor de intensidad (0-255)"
        )

        plt.ylabel(
            "Frecuencia"
        )

        plt.show()

# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    ventana = tk.Tk()
    app = AppPDI(
        ventana
    )
    ventana.mainloop()
