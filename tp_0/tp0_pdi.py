"""
TP 0 - Interfaz gráfica para Procesamiento Digital de Imágenes

Objetivos:
- Abrir una imagen y visualizarla.
- Mostrar una imagen de entrada y una imagen resultado.
- Pasar el resultado al espacio de entrada.
- Restaurar la imagen original en la entrada.
- Guardar la imagen resultado.
- Visualizar el histograma de la entrada o del resultado.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image, ImageTk

class AppPDI:

    def __init__(self, ventana):

        self.ventana = ventana

        self.ventana.title(
            "PDI - Tkinter + NumPy"
        )

        self.ventana.geometry(
            "1100x650"
        )

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
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("BMP", "*.bmp")
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


        # Elegimos cuál de las dos imágenes analizar.
        if self.histograma_de.get() == "Entrada":

            imagen = self.imagen_entrada
            nombre = "Entrada"

        else:

            imagen = self.imagen_procesada
            nombre = "Resultado"


        # Para este primer histograma convertimos la imagen
        # RGB a una intensidad promedio.
        gris = imagen.mean(
            axis=2
        )


        # Matplotlib muestra el histograma en una ventana aparte.
        plt.figure(
            f"Histograma - {nombre}"
        )

        plt.hist(
            gris.reshape(-1),
            bins=256,
            range=(0, 1)
        )

        plt.title(
            f"Histograma - Imagen {nombre}"
        )

        plt.xlabel(
            "Intensidad"
        )

        plt.ylabel(
            "Cantidad de píxeles"
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
