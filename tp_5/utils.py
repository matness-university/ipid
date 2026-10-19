"""
Funciones de Procesamiento Digital de Imágenes.

Este módulo contiene las funciones utilizadas por el TP5
para realizar procesamiento morfológico en niveles de gris
con un elemento estructurante de 3x3.
"""

import numpy as np

RGB_TO_YIQ = np.array(
    [
        [0.299, 0.587, 0.114],
        [0.595716, -0.274453, -0.321263],
        [0.211456, -0.522591, 0.311135],
    ]
)


def rgb_to_yiq(image):
    return image @ RGB_TO_YIQ.T


# ============================================================
# VECINDAD 3x3
# ============================================================


def neighborhood_filter(image, function, size=3):
    """
    Recorre la imagen y, para cada pixel, aplica una
    función sobre los valores de su vecindad.

    El recorrido es el mismo que en la convolución del TP4,
    pero en lugar de multiplicar por un kernel se elige un
    valor de la vecindad (mínimo, máximo o mediana).

    Para tratar los bordes se repiten las filas y columnas
    de los extremos de la imagen, igual que en el TP4.
    """

    pad = size // 2

    # Repetimos los valores de los bordes de la imagen.
    padded_image = np.pad(image, ((pad, pad), (pad, pad)), mode="edge")

    result = np.zeros_like(image, dtype=float)

    # Recorremos cada pixel de la imagen.
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # Vecindad 3x3 centrada en el pixel (i, j).
            window = padded_image[i : i + size, j : j + size]

            result[i, j] = function(window)

    return result


# ============================================================
# OPERACIONES BÁSICAS
# ============================================================


def erosion(image):
    """
    Erosión en niveles de gris.

    Cada pixel toma el mínimo valor de luminancia
    de su vecindad 3x3.
    """

    return neighborhood_filter(image, np.min)


def dilation(image):
    """
    Dilatación en niveles de gris.

    Cada pixel toma el máximo valor de luminancia
    de su vecindad 3x3.
    """

    return neighborhood_filter(image, np.max)


# ============================================================
# OPERACIONES COMBINADAS
# ============================================================


def opening(image):
    """
    Apertura: erosión seguida por dilatación.

    Elimina detalles claros de menor tamaño que el
    elemento estructurante.
    """

    return dilation(erosion(image))


def closing(image):
    """
    Cierre: dilatación seguida por erosión.

    Rellena detalles oscuros (huecos) de menor tamaño
    que el elemento estructurante.
    """

    return erosion(dilation(image))


def outer_border(image):
    """
    Borde exterior: dilatación menos original.
    """

    return dilation(image) - image


def inner_border(image):
    """
    Borde interior: original menos erosión.
    """

    return image - erosion(image)


def morphological_gradient(image):
    """
    Gradiente morfológico: dilatación menos erosión.

    Es la suma del borde exterior y el borde interior.
    """

    return dilation(image) - erosion(image)


# ============================================================
# FILTRO DE MEDIANA
# ============================================================


def median(image):
    """
    Filtro de mediana.

    Cada pixel toma la mediana de los 9 valores
    de luminancia de su vecindad 3x3.
    """

    return neighborhood_filter(image, np.median)
