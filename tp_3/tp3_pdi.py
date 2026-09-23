"""
TP 3 - Operaciones de luminancia

Objetivos:
- Abrir y visualizar una imagen.
- Trabajar con la luminancia en el espacio YIQ.
- Aplicar filtro raíz cuadrada.
- Aplicar filtro cuadrado.
- Aplicar una transformación lineal a trozos.

La interfaz utiliza como base lo desarrollado
en los trabajos prácticos anteriores.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image, ImageTk

import utils as pdi


class AppPDI:

    def __init__(self, ventana):

        self.ventana = ventana
        self.ventana.title("TP 3 - Operaciones de luminancia")
        self.ventana.geometry("1000x650")

        # Imágenes utilizadas por la aplicación.
        self.imagen_original = None
        self.imagen_entrada = None
        self.imagen_procesada = None

        self.crear_interfaz()


    def crear_interfaz(self):

        barra = tk.Frame(
            self.ventana
        )

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

        panel = tk.Frame(
            self.ventana
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        zona_imagenes = tk.Frame(
            panel
        )

        zona_imagenes.pack(
            side="left",
            fill="both",
            expand=True
        )

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
            text="IMAGEN DE ENTRADA",
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

        controles = tk.Frame(
            panel
        )

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

        boton_pasar = tk.Button(
            controles,
            text="Usar resultado\ncomo entrada",
            command=self.pasar_resultado_a_entrada
        )

        boton_pasar.pack(
            fill="x",
            pady=10
        )

        tk.Label(
            controles,
            text="Filtro:"
        ).pack(
            pady=(20, 5)
        )

        self.operacion = tk.StringVar()

        self.operacion.set(
            "Sin procesamiento"
        )

        opciones = [
            "Sin procesamiento",
            "Raíz",
            "Cuadrado",
            "Lineal a trozos"
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

        tk.Label(
            controles,
            text="Y min:"
        ).pack(
            pady=(20, 5)
        )

        self.y_min = tk.StringVar()
        self.y_min.set("0.2")

        entrada_y_min = tk.Entry(
            controles,
            textvariable=self.y_min
        )

        entrada_y_min.pack(
            fill="x",
            pady=5
        )

        tk.Label(
            controles,
            text="Y max:"
        ).pack(
            pady=(10, 5)
        )

        self.y_max = tk.StringVar()
        self.y_max.set("0.8")

        entrada_y_max = tk.Entry(
            controles,
            textvariable=self.y_max
        )

        entrada_y_max.pack(
            fill="x",
            pady=5
        )

        boton_aplicar = tk.Button(
            controles,
            text="Aplicar filtro",
            command=self.aplicar_operacion
        )

        boton_aplicar.pack(
            fill="x",
            pady=15
        )

        tk.Label(
            controles,
            text="Histograma de luminancia:"
        ).pack(
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
                (
                    "Imágenes",
                    "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"
                )
            ]
        )

        if not ruta:
            return

        imagen_pil = Image.open(
            ruta
        ).convert("RGB")

        # Trabajamos con los valores RGB normalizados entre 0 y 1.
        image = (
            np.array(imagen_pil) / 255.0
        )

        self.imagen_original = image

        self.imagen_entrada = (
            self.imagen_original.copy()
        )

        self.imagen_procesada = (
            self.imagen_original.copy()
        )

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
    # APLICAR OPERACIÓN
    # ========================================================

    def aplicar_operacion(self):

        if self.imagen_entrada is None:

            messagebox.showwarning(
                "Atención",
                "Primero abrí una imagen."
            )

            return

        operacion = self.operacion.get()

        image = self.imagen_entrada

        if operacion == "Sin procesamiento":

            result = image.copy()

        elif operacion == "Raíz":

            yiq = pdi.rgb_to_yiq(
                image
            )

            yiq = pdi.square_root_luminance(
                yiq
            )

            result = pdi.yiq_to_rgb(
                yiq
            )

        elif operacion == "Cuadrado":

            yiq = pdi.rgb_to_yiq(
                image
            )

            yiq = pdi.square_luminance(
                yiq
            )

            result = pdi.yiq_to_rgb(
                yiq
            )

        elif operacion == "Lineal a trozos":

            try:

                y_min = float(
                    self.y_min.get()
                )

                y_max = float(
                    self.y_max.get()
                )

            except ValueError:

                messagebox.showwarning(
                    "Atención",
                    "Y min e Y max deben ser números."
                )

                return

            # Y trabaja normalizada en el intervalo [0, 1].
            if not (
                0 <= y_min < y_max <= 1
            ):

                messagebox.showwarning(
                    "Atención",
                    "Debe cumplirse 0 <= Y min < Y max <= 1."
                )

                return

            yiq = pdi.rgb_to_yiq(
                image
            )

            yiq = pdi.piecewise_linear_luminance(
                yiq,
                y_min,
                y_max
            )

            result = pdi.yiq_to_rgb(
                yiq
            )

        self.imagen_procesada = result

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

        imagen_uint8 = (
            np.clip(
                array_imagen,
                0,
                1
            ) * 255
        ).astype(np.uint8)

        imagen_pil = Image.fromarray(
            imagen_uint8
        )

        # El thumbnail modifica solamente la visualización.
        imagen_pil.thumbnail(
            (350, 500)
        )

        foto = ImageTk.PhotoImage(
            imagen_pil
        )

        # Conservamos la referencia para que Tkinter
        # pueda mantener visible la imagen.
        label.foto = foto

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

        imagen_uint8 = (
            np.clip(
                self.imagen_procesada,
                0,
                1
            ) * 255
        ).astype(np.uint8)

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
    # HISTOGRAMA DE LUMINANCIA
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

        # El histograma se calcula sobre la luminancia Y.
        yiq = pdi.rgb_to_yiq(
            image
        )

        luminance = yiq[:, :, 0]

        plt.hist(
            luminance.reshape(-1),
            bins=32,
            range=(0, 1)
        )

        plt.title(
            f"Histograma de luminancia - {nombre}"
        )

        plt.xlabel(
            "Luminancia Y"
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