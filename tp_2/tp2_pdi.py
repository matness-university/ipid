"""
TP 2 - Aritmética de píxeles

Objetivos:
- Realizar operaciones aritméticas entre dos imágenes.
- Implementar cuasi-suma y cuasi-resta en RGB.
- Implementar cuasi-suma y cuasi-resta en YIQ.
- Implementar producto y cociente entre imágenes.
- Implementar resta utilizando valor absoluto.
- Implementar las operaciones if-darker e if-lighter.

La interfaz utiliza como base lo desarrollado en los TP's 0 y 1.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image, ImageTk

# ============================================================
# FUNCIONES DE PDI
# ============================================================

# Matriz de transformación RGB -> YIQ
RGB_TO_YIQ = np.array([
    [0.299,     0.587,      0.114],
    [0.595716, -0.274453,  -0.321263],
    [0.211456, -0.522591,   0.311135]
])

# Matriz de transformación YIQ -> RGB
YIQ_TO_RGB = np.array([
    [1.0,  0.9663,  0.6210],
    [1.0, -0.2721, -0.6474],
    [1.0, -1.1070,  1.7046]
])

def rgb_to_yiq(image):
    """
    Convierte una imagen RGB normalizada al espacio YIQ.
    """
    # Aplicamos la transformación matricial a cada píxel RGB.
    return image @ RGB_TO_YIQ.T


def yiq_to_rgb(image):
    """
    Convierte una imagen YIQ nuevamente al espacio RGB.
    """
    # Aplicamos la transformación matricial a cada píxel YIQ.
    result = image @ YIQ_TO_RGB.T
    return np.clip(
        result,
        0,
        1
    )


def change_luminance_saturation(yiq, a, b):
    """
    Modifica independientemente la luminancia y la saturación
    de una imagen en el espacio YIQ.

    a: coeficiente de luminancia.
    b: coeficiente de saturación.
    """

    result = yiq.copy()

    # Y representa la luminancia.
    result[:, :, 0] = (
        result[:, :, 0] * a
    )

    # I y Q representan la crominancia.
    result[:, :, 1] = (
        result[:, :, 1] * b
    )

    result[:, :, 2] = (
        result[:, :, 2] * b
    )

    # Controlamos los rangos indicados para YIQ.
    result[:, :, 0] = np.clip(
        result[:, :, 0],
        0,
        1
    )

    result[:, :, 1] = np.clip(
        result[:, :, 1],
        -0.5957,
        0.5957
    )

    result[:, :, 2] = np.clip(
        result[:, :, 2],
        -0.5226,
        0.5226
    )

    return result


def grayscale(image):
    """
    Convierte una imagen RGB a escala de grises.

    La imagen llega como array:
        alto x ancho x 3

    El promedio de los tres canales genera un único valor
    de intensidad.

    Después repetimos ese canal 3 veces para conservar
    el formato RGB.
    """

    gray = image.mean(axis=2)

    result = np.stack(
        [gray, gray, gray],
        axis=2
    )

    return result


def single_channel(image, channel):
    """
    Conserva solamente un canal RGB.

    channel:
        0 -> R
        1 -> G
        2 -> B
    """

    result = np.zeros_like(image)

    result[:, :, channel] = image[:, :, channel]

    return result


def sum_rgb(image_a, image_b, averaged=False):
    """
    Performs a quasi-sum between two RGB images.
    """

    if averaged:
        result = (
            image_a + image_b
        ) / 2
    else:
        result = (
            image_a + image_b
        )

        result = np.clip(
            result,
            0,
            1
        )

    return result


def sum_yiq(image_a, image_b, averaged=False):
    """
    Realiza una cuasi-suma entre dos imágenes
    trabajando en el espacio YIQ.

    La luminancia Y se suma de forma clampeada
    o promediada.

    La cromaticidad I y Q se obtiene mediante
    una interpolación ponderada por las luminancias.
    """

    yiq_a = rgb_to_yiq(image_a)
    yiq_b = rgb_to_yiq(image_b)

    result = np.zeros_like(yiq_a)

    ya = yiq_a[:, :, 0]
    yb = yiq_b[:, :, 0]

    # ----------------------------------------------------
    # Luminancia
    # ----------------------------------------------------

    if averaged:
        result[:, :, 0] = (
            ya + yb
        ) / 2
    else:
        result[:, :, 0] = np.clip(
            ya + yb,
            0,
            1
        )

    # ----------------------------------------------------
    # Cromaticidad
    # ----------------------------------------------------

    luminance_sum = (
        ya + yb
    )

    # Evitamos dividir por cero cuando ambos píxeles
    # tienen luminancia cero.
    denominator = np.where(
        luminance_sum == 0,
        1,
        luminance_sum
    )

    result[:, :, 1] = (
        ya * yiq_a[:, :, 1]
        + yb * yiq_b[:, :, 1]
    ) / denominator

    result[:, :, 2] = (
        ya * yiq_a[:, :, 2]
        + yb * yiq_b[:, :, 2]
    ) / denominator

    return yiq_to_rgb(
        result
    )


def diff_rgb(image_a, image_b, averaged=False):
    """
    Performs a quasi-difference between two RGB images.
    """

    if averaged:
        result = (
            image_a - image_b + 1
        ) / 2
    else:
        result = (
            image_a - image_b
        )

        result = np.clip(
            result,
            0,
            1
        )

    return result


def abs_diff_rgb(image_a, image_b):
    """
    Performs an absolute difference between two RGB images.
    """

    result = np.abs(
        image_a - image_b
    )

    return result


def diff_yiq(image_a, image_b, averaged=False):
    """
    Realiza una cuasi-resta entre dos imágenes
    trabajando en el espacio YIQ.
    """

    yiq_a = rgb_to_yiq(image_a)
    yiq_b = rgb_to_yiq(image_b)

    result = np.zeros_like(yiq_a)

    ya = yiq_a[:, :, 0]
    yb = yiq_b[:, :, 0]

    # ----------------------------------------------------
    # Resta promediada
    # ----------------------------------------------------

    if averaged:
        result[:, :, 0] = (
            ya - yb + 1
        ) / 2

        result[:, :, 1] = (
            yiq_a[:, :, 1]
            - yiq_b[:, :, 1]
        ) / 2

        result[:, :, 2] = (
            yiq_a[:, :, 2]
            - yiq_b[:, :, 2]
        ) / 2

    # ----------------------------------------------------
    # Resta clampeada
    # ----------------------------------------------------

    else:
        result[:, :, 0] = np.clip(
            ya - yb,
            0,
            1
        )

        result[:, :, 1] = (
            yiq_a[:, :, 1]
            - yiq_b[:, :, 1]
        )

        result[:, :, 2] = (
            yiq_a[:, :, 2]
            - yiq_b[:, :, 2]
        )

    # Controlamos los rangos de I y Q.
    result[:, :, 1] = np.clip(
        result[:, :, 1],
        -0.5957,
        0.5957
    )

    result[:, :, 2] = np.clip(
        result[:, :, 2],
        -0.5226,
        0.5226
    )

    return yiq_to_rgb(
        result
    )


def product_rgb(image_a, image_b):
    """
    Realiza el producto píxel a píxel
    entre dos imágenes RGB.
    """

    result = (
        image_a * image_b
    )

    return result


def quotient_rgb(image_a, image_b):
    """
    Realiza el cociente píxel a píxel
    entre dos imágenes RGB.

    Se agrega un nivel mínimo de intensidad
    al divisor para evitar la división por cero.
    """

    divisor = image_b + 1 / 255

    result = image_a / divisor

    return np.clip(
        result,
        0,
        1
    )


def if_lighter(image_a, image_b):
    """
    Conserva, para cada posición, el píxel de la imagen
    que tenga mayor luminancia.

    La comparación se realiza utilizando Y en el
    espacio YIQ.
    """

    yiq_a = rgb_to_yiq(
        image_a
    )

    yiq_b = rgb_to_yiq(
        image_b
    )

    # Comparamos la luminancia Y de ambas imágenes.
    condition = (
        yiq_a[:, :, 0] > yiq_b[:, :, 0]
    )

    # Repetimos la condición para los tres componentes
    # Y, I y Q.
    condition = condition[:, :, np.newaxis]

    # Si Y de A es mayor, conservamos el píxel YIQ
    # completo de A. En caso contrario, el de B.
    result = np.where(
        condition,
        yiq_a,
        yiq_b
    )

    return yiq_to_rgb(
        result
    )


def if_darker(image_a, image_b):
    """
    Conserva, para cada posición, el píxel de la imagen
    que tenga menor luminancia.

    La comparación se realiza utilizando Y en el
    espacio YIQ.
    """

    yiq_a = rgb_to_yiq(
        image_a
    )

    yiq_b = rgb_to_yiq(
        image_b
    )

    # Comparamos la luminancia Y de ambas imágenes.
    condition = (
        yiq_a[:, :, 0] < yiq_b[:, :, 0]
    )

    # Repetimos la condición para los tres componentes
    # Y, I y Q.
    condition = condition[:, :, np.newaxis]

    # Si Y de A es menor, conservamos el píxel YIQ
    # completo de A. En caso contrario, el de B.
    result = np.where(
        condition,
        yiq_a,
        yiq_b
    )

    return yiq_to_rgb(
        result
    )


class AppPDI:

    def __init__(self, ventana):

        self.ventana = ventana
        self.ventana.title("PDI - Tkinter + NumPy")

        self.ventana.geometry("1100x650")

        # ----------------------------------------------------
        # Imágenes de la aplicación.
        #
        # imagen_original:
        #     Copia original de la imagen A.
        #
        # imagen_entrada:
        #     Imagen A utilizada en los procesamientos.
        #
        # imagen_segunda:
        #     Imagen B utilizada en las operaciones entre
        #     dos imágenes.
        #
        # imagen_procesada:
        #     Imagen C obtenida como resultado.
        # ----------------------------------------------------

        self.imagen_original = None
        self.imagen_entrada = None
        self.imagen_segunda = None
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
            text="Abrir imagen A",
            command=self.abrir_imagen
        )

        boton_abrir.pack(
            side="left",
            padx=5
        )

        boton_abrir_segunda = tk.Button(
            barra,
            text="Abrir imagen B",
            command=self.abrir_segunda_imagen
        )

        boton_abrir_segunda.pack(
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
            text="IMAGEN A",
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
        # Segunda imagen
        # ----------------------------------------------------

        frame_segunda = tk.Frame(
            zona_imagenes
        )

        frame_segunda.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        titulo_segunda = tk.Label(
            frame_segunda,
            text="IMAGEN B",
            font=("Arial", 11, "bold")
        )

        titulo_segunda.pack(
            pady=5
        )

        self.label_segunda = tk.Label(
            frame_segunda,
            text="Abrí una segunda imagen",
            bg="#dddddd"
        )

        self.label_segunda.pack(
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
            text="RESULTADO C",
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
            "Solo canal B",
            "Suma RGB clampeada",
            "Suma RGB promediada",
            "Resta RGB clampeada",
            "Resta RGB promediada",
            "Resta RGB absoluta",
            "Suma YIQ clampeada",
            "Suma YIQ promediada",
            "Resta YIQ clampeada",
            "Resta YIQ promediada",
            "Producto RGB",
            "Cociente RGB",
            "If-lighter",
            "If-darker"
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

        image = (
            np.array(imagen_pil) / 255.0
        )

        if self.imagen_segunda is not None:
            if image.shape != self.imagen_segunda.shape:
                messagebox.showwarning(
                    "Atención",
                    "Las imágenes deben tener la misma resolución."
                )
                return

        self.imagen_original = image

        # La imagen A queda guardada como original
        # y también se utiliza como imagen de entrada.
        self.imagen_entrada = (
            self.imagen_original.copy()
        )

        # Al cargar A, inicialmente mostramos A
        # también en el espacio de result.
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
    # ABRIR SEGUNDA IMAGEN
    # ========================================================

    def abrir_segunda_imagen(self):

        ruta = filedialog.askopenfilename(
            title="Seleccionar segunda imagen",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")
            ]
        )

        if not ruta:
            return

        imagen_pil = Image.open(
            ruta
        ).convert("RGB")

        image = (
            np.array(imagen_pil) / 255.0
        )

        # Las operaciones del TP2 requieren imágenes
        # con la misma resolución.
        if self.imagen_entrada is not None:
            if image.shape != self.imagen_entrada.shape:
                messagebox.showwarning(
                    "Atención",
                    "Las imágenes deben tener la misma resolución."
                )
                return

        self.imagen_segunda = image

        self.mostrar_imagen(
            self.imagen_segunda,
            self.label_segunda
        )

        self.estado.config(
            text="Segunda imagen cargada correctamente."
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

        # Convertimos la imagen de entrada RGB -> YIQ.
        imagen_yiq = rgb_to_yiq(
            self.imagen_entrada
        )

        # Modificamos luminancia y saturación en YIQ.
        imagen_yiq = change_luminance_saturation(
            imagen_yiq,
            a,
            b
        )

        # Convertimos el resultado YIQ -> RGB.
        self.imagen_procesada = yiq_to_rgb(
            imagen_yiq
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

        image = self.imagen_entrada

        # ----------------------------------------------------
        # Acá empieza la conexión entre Tkinter y PDI.
        # ----------------------------------------------------

        if operacion == "Sin procesamiento":

            result = image.copy()

        elif operacion == "Escala de grises":

            result = grayscale(
                image
            )

        elif operacion == "Solo canal R":

            result = single_channel(
                image,
                0
            )

        elif operacion == "Solo canal G":

            result = single_channel(
                image,
                1
            )

        elif operacion == "Solo canal B":

            result = single_channel(
                image,
                2
            )

        elif operacion == "Suma RGB clampeada":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = sum_rgb(
                self.imagen_entrada,
                self.imagen_segunda,
                averaged=False
            )

        elif operacion == "Suma RGB promediada":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = sum_rgb(
                self.imagen_entrada,
                self.imagen_segunda,
                averaged=True
            )

        elif operacion == "Resta RGB clampeada":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = diff_rgb(
                self.imagen_entrada,
                self.imagen_segunda,
                averaged=False
            )

        elif operacion == "Resta RGB promediada":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = diff_rgb(
                self.imagen_entrada,
                self.imagen_segunda,
                averaged=True
            )

        elif operacion == "Resta RGB absoluta":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = abs_diff_rgb(
                self.imagen_entrada,
                self.imagen_segunda,
            )

        elif operacion == "Suma YIQ clampeada":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = sum_yiq(
                self.imagen_entrada,
                self.imagen_segunda,
                averaged=False
            )

        elif operacion == "Suma YIQ promediada":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = sum_yiq(
                self.imagen_entrada,
                self.imagen_segunda,
                averaged=True
            )

        elif operacion == "Resta YIQ clampeada":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = diff_yiq(
                self.imagen_entrada,
                self.imagen_segunda,
                averaged=False
            )

        elif operacion == "Resta YIQ promediada":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = diff_yiq(
                self.imagen_entrada,
                self.imagen_segunda,
                averaged=True
            )

        elif operacion == "Producto RGB":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = product_rgb(
                self.imagen_entrada,
                self.imagen_segunda
            )

        elif operacion == "Cociente RGB":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = quotient_rgb(
                self.imagen_entrada,
                self.imagen_segunda
            )

        elif operacion == "If-lighter":
            
            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = if_lighter(
                self.imagen_entrada,
                self.imagen_segunda
            )

        elif operacion == "If-darker":

            if self.imagen_segunda is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero abrí la segunda imagen."
                )
                return

            result = if_darker(
                self.imagen_entrada,
                self.imagen_segunda
            )

        # Guardamos el resultado.
        self.imagen_procesada = result

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
            (280, 500)
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
            image = self.imagen_entrada
            nombre = "Entrada"
        else:
            if self.imagen_procesada is None:
                messagebox.showwarning(
                    "Atención",
                    "Primero generá un resultado."
                )
                return
            
            image = self.imagen_procesada
            nombre = "Resultado"

        gray = image.mean(
            axis=2
        )

        intensidades = (
            gray * 255
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
