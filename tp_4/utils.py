"""
Funciones de Procesamiento Digital de Imágenes.

Este módulo contiene las funciones utilizadas por el TP4
para realizar procesamiento por convolución.
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
# CONVOLUCIÓN
# ============================================================


def convolution(image, kernel):
    """
    Aplica un kernel de convolución sobre una imagen
    en niveles de gris.

    Para tratar los bordes se repiten las filas y columnas
    de los extremos de la imagen.
    """

    kernel_height, kernel_width = kernel.shape

    pad_y = kernel_height // 2
    pad_x = kernel_width // 2

    # Repetimos los valores de los bordes de la imagen.
    padded_image = np.pad(image, ((pad_y, pad_y), (pad_x, pad_x)), mode="edge")

    # En la convolución el kernel se rota 180 grados.
    rotated_kernel = np.rot90(kernel, 2)

    result = np.zeros_like(image, dtype=float)

    # Recorremos cada pixel de la imagen.
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            value = 0.0

            # Recorremos el kernel.
            for ki in range(kernel_height):
                for kj in range(kernel_width):
                    value += padded_image[i + ki, j + kj] * rotated_kernel[ki, kj]
            result[i, j] = value
    return result


# ============================================================
# FILTROS PASABAJOS
# ============================================================


def flat_kernel(size):
    """
    Genera un kernel pasabajos plano.

    Todos los coeficientes tienen el mismo peso
    y la suma total del kernel es 1.
    """

    kernel = np.ones((size, size), dtype=float)

    return kernel / kernel.sum()


def bartlett_kernel(size):
    """
    Genera un kernel pasabajos Bartlett.

    Los coeficientes aumentan hacia el centro
    y luego disminuyen simétricamente.
    El kernel se normaliza para que su suma sea 1.
    """

    sequence = (size + 1) / 2 - np.abs(np.arange(size) - size // 2)

    kernel = np.outer(sequence, sequence)

    return kernel / kernel.sum()


def gaussian_kernel(size):
    """
    Genera un kernel pasabajos Gaussiano utilizando
    los coeficientes del triángulo de Pascal.

    El kernel se normaliza para que su suma sea 1.
    """

    sequence = np.array([1.0])

    for _ in range(size - 1):
        sequence = np.convolve(sequence, [1.0, 1.0])

    kernel = np.outer(sequence, sequence)

    return kernel / kernel.sum()


# ============================================================
# FILTROS PASAALTOS
# ============================================================


def laplacian_kernel_v4():
    """
    Genera un kernel Laplaciano utilizando
    los 4 vecinos ortogonales.
    """

    return np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=float)


def laplacian_kernel_v8():
    """
    Genera un kernel Laplaciano utilizando
    los 8 vecinos.
    """

    return np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=float)


def sobel_kernel(direction):
    """
    Retorna el kernel Sobel 3x3 correspondiente
    a una de las ocho orientaciones.
    """

    if direction == "E":
        return np.array([[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]])

    elif direction == "NE":
        return np.array([[0.0, 1.0, 2.0], [-1.0, 0.0, 1.0], [-2.0, -1.0, 0.0]])

    elif direction == "N":
        return np.array([[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]])

    elif direction == "NW":
        return np.array([[2.0, 1.0, 0.0], [1.0, 0.0, -1.0], [0.0, -1.0, -2.0]])

    elif direction == "W":
        return np.array([[1.0, 0.0, -1.0], [2.0, 0.0, -2.0], [1.0, 0.0, -1.0]])

    elif direction == "SW":
        return np.array([[0.0, -1.0, -2.0], [1.0, 0.0, -1.0], [2.0, 1.0, 0.0]])

    elif direction == "S":
        return np.array([[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0]])

    elif direction == "SE":
        return np.array([[-2.0, -1.0, 0.0], [-1.0, 0.0, 1.0], [0.0, 1.0, 2.0]])

    raise ValueError("Dirección Sobel no válida")


# ============================================================
# FILTROS POR FRECUENCIA DE CORTE
# ============================================================


def low_pass_kernel(cutoff_frequency, size=7):
    """
    Genera un kernel pasabajos a partir de una
    frecuencia de corte normalizada.
    """

    center = size // 2
    sequence = np.zeros(size, dtype=float)

    for i in range(size):
        n = i - center

        if n == 0:
            sequence[i] = 2 * cutoff_frequency
        else:
            sequence[i] = np.sin(2 * np.pi * cutoff_frequency * n) / (np.pi * n)

    sequence = sequence / sequence.sum()

    kernel = np.outer(sequence, sequence)
    kernel = kernel / kernel.sum()

    return kernel


def high_pass_kernel(cutoff_frequency, size=7):
    """
    Genera un kernel pasaaltos a partir de un
    kernel pasabajos mediante inversión espectral.
    """

    low_pass = low_pass_kernel(cutoff_frequency, size)

    impulse = np.zeros((size, size), dtype=float)

    center = size // 2
    impulse[center, center] = 1.0

    return impulse - low_pass


# ============================================================
# FILTRO PASABANDA
# ============================================================


def band_pass_kernel():
    """
    Genera un filtro pasabanda mediante diferencia
    de Gaussianas (DoG).
    """

    gaussian_3 = gaussian_kernel(3)
    gaussian_5 = gaussian_kernel(5)

    gaussian_3 = np.pad(gaussian_3, ((1, 1), (1, 1)), mode="constant")

    return gaussian_3 - gaussian_5
