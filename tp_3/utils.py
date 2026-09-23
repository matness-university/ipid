"""
Funciones de Procesamiento Digital de Imágenes.

Este módulo contiene las funciones utilizadas por el TP3
para trabajar con el espacio de color YIQ y realizar
operaciones sobre la luminancia.
"""

import numpy as np


# ============================================================
# CONVERSIÓN ENTRE ESPACIOS DE COLOR
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
    return image @ RGB_TO_YIQ.T


def yiq_to_rgb(image):
    """
    Convierte una imagen YIQ nuevamente al espacio RGB.
    """
    result = image @ YIQ_TO_RGB.T

    return np.clip(
        result,
        0,
        1
    )


# ============================================================
# OPERACIONES DE LUMINANCIA
# ============================================================

def square_root_luminance(yiq):
    """
    Aplica la función raíz cuadrada sobre la luminancia Y.

    La raíz cuadrada aumenta principalmente los valores
    bajos de luminancia.
    """

    result = yiq.copy()

    result[:, :, 0] = np.sqrt(
        result[:, :, 0]
    )

    return result


def square_luminance(yiq):
    """
    Aplica la función cuadrado sobre la luminancia Y.

    El cuadrado disminuye los valores de luminancia
    comprendidos entre 0 y 1.
    """

    result = yiq.copy()

    result[:, :, 0] = np.square(
        result[:, :, 0]
    )

    return result


def piecewise_linear_luminance(yiq, y_min, y_max):
    """
    Aplica una transformación lineal a trozos
    sobre la luminancia Y.

    Y < y_min:
        Y' = 0

    y_min <= Y <= y_max:
        Y' = (Y - y_min) / (y_max - y_min)

    Y > y_max:
        Y' = 1
    """

    result = yiq.copy()

    y = result[:, :, 0]

    new_y = np.zeros_like(
        y
    )

    # Los valores mayores al máximo pasan a 1.
    new_y[y > y_max] = 1

    # Seleccionamos los valores comprendidos
    # entre y_min e y_max.
    middle = (
        (y >= y_min)
        & (y <= y_max)
    )

    # Transformación lineal del intervalo
    # [y_min, y_max] al intervalo [0, 1].
    new_y[middle] = (
        (y[middle] - y_min)
        / (y_max - y_min)
    )

    # Reemplazamos solamente la luminancia.
    # Las componentes I y Q permanecen sin cambios.
    result[:, :, 0] = new_y

    return result