"""
TP 6 - Segmentación

Objetivos:
- Abrir y visualizar una imagen.
- Trabajar con la luminancia en el espacio YIQ.
- Punto 1: binarizar la imagen con 50 % de pixels negros
  y blancos, con dos modas y distancia mínima, y con Otsu,
  y comparar los umbrales obtenidos.
- Punto 2: encontrar los bordes con Laplaciano, borde
  morfológico, marching squares y Teh-Chin.
- Copiar el resultado en la entrada para aplicar
  dos o más procesamientos en secuencia
  (por ejemplo, mediana y luego Laplaciano).

La interfaz utiliza como base lo desarrollado
en los trabajos prácticos anteriores.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np

from PIL import Image, ImageTk

import utils as pdi


class AppPDI:

    def __init__(self, ventana):

        self.ventana = ventana
        self.ventana.title("TP 6 - Segmentación")
        self.ventana.geometry("1000x650")

        # Imágenes utilizadas por la aplicación.
        self.imagen_original = None
        self.imagen_entrada = None
        self.imagen_procesada = None

        self.crear_interfaz()

    def crear_interfaz(self):

        barra = tk.Frame(self.ventana)

        barra.pack(side="top", fill="x", padx=10, pady=10)

        boton_abrir = tk.Button(barra, text="Abrir imagen", command=self.abrir_imagen)

        boton_abrir.pack(side="left", padx=5)

        boton_restaurar = tk.Button(
            barra, text="Restaurar original", command=self.restaurar_original
        )

        boton_restaurar.pack(side="left", padx=5)

        boton_guardar = tk.Button(
            barra, text="Guardar resultado", command=self.guardar_resultado
        )

        boton_guardar.pack(side="left", padx=5)

        panel = tk.Frame(self.ventana)

        panel.pack(fill="both", expand=True, padx=10, pady=10)

        zona_imagenes = tk.Frame(panel)

        zona_imagenes.pack(side="left", fill="both", expand=True)

        frame_entrada = tk.Frame(zona_imagenes)

        frame_entrada.pack(side="left", fill="both", expand=True, padx=5)

        titulo_entrada = tk.Label(
            frame_entrada, text="IMAGEN DE ENTRADA", font=("Arial", 11, "bold")
        )

        titulo_entrada.pack(pady=5)

        self.label_entrada = tk.Label(
            frame_entrada, text="Abrí una imagen para comenzar", bg="#dddddd"
        )

        self.label_entrada.pack(fill="both", expand=True)

        frame_resultado = tk.Frame(zona_imagenes)

        frame_resultado.pack(side="left", fill="both", expand=True, padx=5)

        titulo_resultado = tk.Label(
            frame_resultado, text="RESULTADO", font=("Arial", 11, "bold")
        )

        titulo_resultado.pack(pady=5)

        self.label_resultado = tk.Label(
            frame_resultado, text="El resultado aparecerá aquí", bg="#dddddd"
        )

        self.label_resultado.pack(fill="both", expand=True)

        controles = tk.Frame(panel)

        controles.pack(side="right", fill="y", padx=10)

        titulo_controles = tk.Label(
            controles, text="Controles", font=("Arial", 14, "bold")
        )

        titulo_controles.pack(pady=10)

        boton_pasar = tk.Button(
            controles,
            text="Usar resultado\ncomo entrada",
            command=self.pasar_resultado_a_entrada,
        )

        boton_pasar.pack(fill="x", pady=10)

        tk.Label(controles, text="Operación:").pack(pady=(20, 5))

        self.operacion = tk.StringVar()

        self.operacion.set("Sin procesamiento")

        opciones = [
            "Sin procesamiento",
            "Binarizar 50% / 50%",
            "Binarizar por dos modas",
            "Binarizar por Otsu",
            "Mediana",
            "Laplaciano v4",
            "Laplaciano v8",
            "Borde interior",
            "Borde exterior",
            "Gradiente morfológico",
            "Marching squares (orden 0)",
            "Marching squares (orden 1)",
            "Teh-Chin",
        ]

        menu = tk.OptionMenu(controles, self.operacion, *opciones)

        menu.pack(fill="x", pady=5)

        boton_aplicar = tk.Button(
            controles, text="Aplicar operación", command=self.aplicar_operacion
        )

        boton_aplicar.pack(fill="x", pady=15)

        self.estado = tk.Label(self.ventana, text="Listo.", anchor="w")

        self.estado.pack(side="bottom", fill="x", padx=10, pady=10)

    # ========================================================
    # ABRIR IMAGEN
    # ========================================================

    def abrir_imagen(self):

        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")],
        )

        if not ruta:
            return

        imagen_pil = Image.open(ruta).convert("RGB")

        # Trabajamos con los valores RGB normalizados entre 0 y 1.
        image = np.array(imagen_pil) / 255.0

        self.imagen_original = image

        self.imagen_entrada = self.imagen_original.copy()

        self.imagen_procesada = self.imagen_original.copy()

        self.mostrar_imagen(self.imagen_entrada, self.label_entrada)

        self.mostrar_imagen(self.imagen_procesada, self.label_resultado)

        self.estado.config(text="Imagen cargada correctamente.")

    # ========================================================
    # APLICAR OPERACIÓN
    # ========================================================

    def aplicar_operacion(self):

        if self.imagen_entrada is None:

            messagebox.showwarning("Atención", "Primero abrí una imagen.")

            return

        operacion = self.operacion.get()

        image = self.imagen_entrada

        # El TP6 trabaja sobre la luminancia Y.
        yiq = pdi.rgb_to_yiq(image)

        luminance = np.clip(yiq[:, :, 0], 0, 1)

        # Texto que se muestra en la barra de estado. En las
        # binarizaciones se agrega el umbral usado, para poder
        # comparar los tres métodos (punto 1).
        mensaje = f"Operación aplicada: {operacion}"

        if operacion == "Sin procesamiento":

            result = image.copy()

        elif operacion == "Teh-Chin":

            contorno, dominantes = pdi.dominant_points(luminance)

            if not contorno:

                messagebox.showwarning(
                    "Atención", "No se encontró ninguna figura al binarizar."
                )

                return

            # Es la única operación que devuelve una imagen a color.
            result = pdi.draw_teh_chin(luminance, contorno, dominantes)

            mensaje += (
                f" - {len(contorno)} pixels de contorno,"
                f" {len(dominantes)} puntos dominantes"
            )

        else:

            if operacion == "Binarizar 50% / 50%":

                k = pdi.level_50(luminance)

                filtered = pdi.threshold_levels(luminance, k)

                # Con un solo umbral el 50 % puede no ser exacto,
                # así que se informa cuánto quedó en blanco.
                mensaje += (
                    f" - T = {self.texto_umbral(k / (pdi.LEVELS - 1))},"
                    f" blancos = {filtered.mean() * 100:.1f} %"
                )

            elif operacion == "Binarizar por dos modas":

                # Se buscan las modas una sola vez y se corta a
                # mitad de camino (lo mismo que modes_threshold).
                oscura, clara = pdi.find_modes(luminance)

                t = (oscura + clara) / 2

                filtered = pdi.threshold(luminance, t)

                mensaje += (
                    f" - modas {self.texto_umbral(oscura)} y"
                    f" {self.texto_umbral(clara)}, T = {self.texto_umbral(t)}"
                )

            elif operacion == "Binarizar por Otsu":

                k_star, mu = pdi.otsu(luminance)

                # Se compara en niveles enteros, igual que Otsu
                # (ver threshold_levels en utils.py).
                filtered = pdi.threshold_levels(luminance, k_star)

                t = k_star / (pdi.LEVELS - 1)

                mensaje += f" - T = {self.texto_umbral(t)}, separabilidad = {mu:.2f}"

            elif operacion == "Mediana":

                filtered = pdi.median(luminance)

            elif operacion == "Laplaciano v4":

                filtered = pdi.laplacian_edges(luminance, pdi.LAPLACIAN_V4)

            elif operacion == "Laplaciano v8":

                filtered = pdi.laplacian_edges(luminance, pdi.LAPLACIAN_V8)

            elif operacion == "Borde interior":

                filtered = pdi.inner_border(luminance)

            elif operacion == "Borde exterior":

                filtered = pdi.outer_border(luminance)

            elif operacion == "Gradiente morfológico":

                filtered = pdi.morphological_gradient(luminance)

            elif operacion in (
                "Marching squares (orden 0)",
                "Marching squares (orden 1)",
            ):

                orden = 0 if operacion.endswith("(orden 0)") else 1

                # Curva de nivel en el umbral de Otsu.
                t = pdi.otsu_threshold(luminance)

                segmentos = pdi.marching_squares(luminance, t, order=orden)

                # El resultado se dibuja al doble de tamaño para
                # que se note la diferencia entre orden 0 y 1. La
                # vista previa lo achica, así que la diferencia se
                # ve recién al guardarlo.
                filtered = pdi.draw_segments(luminance.shape, segmentos, scale=2)

                mensaje += (
                    f" - T = {self.texto_umbral(t)} (Otsu)."
                    " Guardá el resultado para ver la diferencia entre orden 0 y 1"
                )

            # Para visualizar el resultado realizamos
            # la coerción al intervalo [0, 1].
            filtered = np.clip(filtered, 0, 1)

            # Conservamos tres canales para mantener el mismo
            # formato utilizado por la interfaz de los TPs
            # anteriores.
            result = np.stack([filtered, filtered, filtered], axis=2)

        self.imagen_procesada = result

        self.mostrar_imagen(self.imagen_procesada, self.label_resultado)

        self.estado.config(text=mensaje)

    def texto_umbral(self, valor):

        # Un umbral en [0, 1] y su nivel equivalente en 0..255.
        nivel = round(valor * (pdi.LEVELS - 1))

        return f"{valor:.3f} (nivel {nivel})"

    # ========================================================
    # MOSTRAR IMAGEN
    # ========================================================

    def mostrar_imagen(self, array_imagen, label):

        imagen_uint8 = (np.clip(array_imagen, 0, 1) * 255).astype(np.uint8)

        imagen_pil = Image.fromarray(imagen_uint8)

        # El thumbnail modifica solamente la visualización.
        imagen_pil.thumbnail((350, 500))

        foto = ImageTk.PhotoImage(imagen_pil)

        # Conservamos la referencia para que Tkinter
        # pueda mantener visible la imagen.
        label.foto = foto

        label.config(image=foto, text="")

    # ========================================================
    # PASAR RESULTADO A ENTRADA
    # ========================================================

    def pasar_resultado_a_entrada(self):

        if self.imagen_procesada is None:

            messagebox.showwarning("Atención", "Primero abrí una imagen.")

            return

        self.imagen_entrada = self.imagen_procesada.copy()

        self.mostrar_imagen(self.imagen_entrada, self.label_entrada)

        self.estado.config(text="La imagen resultado pasó a la entrada.")

    # ========================================================
    # RESTAURAR ORIGINAL
    # ========================================================

    def restaurar_original(self):

        if self.imagen_original is None:
            return

        self.imagen_entrada = self.imagen_original.copy()

        self.imagen_procesada = self.imagen_original.copy()

        self.mostrar_imagen(self.imagen_entrada, self.label_entrada)

        self.mostrar_imagen(self.imagen_procesada, self.label_resultado)

        self.estado.config(text="Imagen original restaurada.")

    # ========================================================
    # GUARDAR RESULTADO
    # ========================================================

    def guardar_resultado(self):

        if self.imagen_procesada is None:

            messagebox.showwarning("Atención", "Primero abrí una imagen.")

            return

        ruta = filedialog.asksaveasfilename(
            title="Guardar imagen procesada",
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )

        if not ruta:
            return

        imagen_uint8 = (np.clip(self.imagen_procesada, 0, 1) * 255).astype(np.uint8)

        imagen_pil = Image.fromarray(imagen_uint8)

        imagen_pil.save(ruta)

        self.estado.config(text="Imagen resultado guardada correctamente.")


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":

    ventana = tk.Tk()

    app = AppPDI(ventana)

    ventana.mainloop()
