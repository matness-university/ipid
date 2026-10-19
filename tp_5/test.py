import numpy as np

from utils import (
    neighborhood_filter,
    erosion,
    dilation,
    opening,
    closing,
    outer_border,
    inner_border,
    morphological_gradient,
    median,
)

np.set_printoptions(precision=2, suppress=True)


print("=== VECINDAD 3x3 ===")

image = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]])

print("Imagen:")
print(image)

# En el pixel central la vecindad es la imagen completa.
print("\nMínimo, máximo y mediana del pixel central:")
print(
    erosion(image)[1, 1],
    dilation(image)[1, 1],
    median(image)[1, 1],
)

assert np.isclose(erosion(image)[1, 1], 0.1)
assert np.isclose(dilation(image)[1, 1], 0.9)
assert np.isclose(median(image)[1, 1], 0.5)

# En la esquina (0, 0) la vecindad usa los bordes repetidos:
# [[0.1, 0.1, 0.2], [0.1, 0.1, 0.2], [0.4, 0.4, 0.5]]
print("\nErosión (en las esquinas se repiten los bordes):")
print(erosion(image))

assert np.isclose(erosion(image)[0, 0], 0.1)
assert np.isclose(dilation(image)[0, 0], 0.5)


print("\n=== EROSIÓN Y DILATACIÓN SOBRE UN PUNTO ===")

point = np.zeros((5, 5))
point[2, 2] = 1.0

print("Imagen:")
print(point)

print("\nErosión (el punto desaparece):")
print(erosion(point))

print("\nDilatación (el punto crece a 3x3):")
print(dilation(point))

assert erosion(point).sum() == 0
assert dilation(point).sum() == 9


print("\n=== EROSIÓN Y DILATACIÓN SOBRE UN CUADRADO 3x3 ===")

square = np.zeros((7, 7))
square[2:5, 2:5] = 1.0

print("Imagen:")
print(square)

print("\nErosión (queda solo el centro):")
print(erosion(square))

print("\nDilatación (crece a 5x5):")
print(dilation(square))

assert erosion(square).sum() == 1
assert dilation(square).sum() == 25


print("\n=== NIVELES DE GRIS ===")

gray = np.array(
    [
        [0.2, 0.2, 0.2, 0.2],
        [0.2, 0.9, 0.5, 0.2],
        [0.2, 0.5, 0.5, 0.2],
        [0.2, 0.2, 0.2, 0.2],
    ]
)

print("Imagen:")
print(gray)

print("\nErosión (mínimo de la vecindad):")
print(erosion(gray))

print("\nDilatación (máximo de la vecindad):")
print(dilation(gray))

assert np.allclose(erosion(gray), 0.2)
assert dilation(gray)[0, 0] == 0.9


print("\n=== APERTURA: ELIMINA RUIDO CLARO ===")

# Cuadrado 3x3 más un pixel blanco aislado (ruido).
noisy = square.copy()
noisy[0, 6] = 1.0

print("Imagen:")
print(noisy)

print("\nApertura:")
print(opening(noisy))

# El ruido desaparece y el cuadrado se conserva.
assert np.allclose(opening(noisy), square)


print("\n=== CIERRE: RELLENA HUECOS OSCUROS ===")

# Cuadrado 5x5 con un hueco negro en el centro.
# Dejamos 2 pixels de margen: ver la prueba siguiente.
holed = np.zeros((9, 9))
holed[2:7, 2:7] = 1.0
holed[4, 4] = 0.0

print("Imagen:")
print(holed)

print("\nCierre:")
print(closing(holed))

expected = np.zeros((9, 9))
expected[2:7, 2:7] = 1.0

assert np.allclose(closing(holed), expected)


print("\n=== EFECTO DE BORDE EN EL CIERRE ===")

# Si la figura está a 1 pixel del borde, la dilatación
# llega hasta el borde de la imagen. Como al erosionar
# repetimos las filas/columnas del borde, la erosión
# ya no puede "despegar" la figura del borde.
near_edge = np.zeros((7, 7))
near_edge[1:6, 1:6] = 1.0

print("Imagen:")
print(near_edge)

print("\nCierre (la figura queda pegada al borde):")
print(closing(near_edge))

assert closing(near_edge).sum() == 49


print("\n=== BORDES MORFOLÓGICOS ===")

block = np.zeros((7, 7))
block[1:6, 1:6] = 1.0

print("Imagen:")
print(block)

print("\nBorde exterior (dilatación - original):")
print(outer_border(block))

print("\nBorde interior (original - erosión):")
print(inner_border(block))

print("\nGradiente (dilatación - erosión):")
print(morphological_gradient(block))

# El borde interior es el contorno del cuadrado 5x5: 25 - 9 = 16 pixels.
assert inner_border(block).sum() == 16

# El gradiente es la suma de ambos bordes.
assert np.allclose(
    morphological_gradient(block), outer_border(block) + inner_border(block)
)

# Ningún borde puede ser negativo.
assert outer_border(block).min() >= 0
assert inner_border(block).min() >= 0


print("\n=== IMAGEN CONSTANTE ===")

constant = np.full((5, 5), 0.5)

for name, function in [
    ("Erosión", erosion),
    ("Dilatación", dilation),
    ("Apertura", opening),
    ("Cierre", closing),
    ("Mediana", median),
]:
    assert np.allclose(function(constant), 0.5), name

for name, function in [
    ("Borde exterior", outer_border),
    ("Borde interior", inner_border),
    ("Gradiente", morphological_gradient),
]:
    assert np.allclose(function(constant), 0.0), name

print("Las operaciones no modifican una imagen constante")
print("y los bordes dan 0 (no hay bordes).")


print("\n=== MEDIANA: RUIDO SAL Y PIMIENTA ===")

salt_pepper = np.full((5, 5), 0.5)
salt_pepper[1, 1] = 1.0  # sal
salt_pepper[3, 3] = 0.0  # pimienta

print("Imagen:")
print(salt_pepper)

print("\nMediana:")
print(median(salt_pepper))

assert np.allclose(median(salt_pepper), 0.5)


print("\n=== MEDIANA vs PROMEDIO EN UN BORDE ===")

edge_image = np.array(
    [
        [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
        [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
        [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
        [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
    ]
)

mean_result = neighborhood_filter(edge_image, np.mean)

print("Imagen:")
print(edge_image)

print("\nPromedio 3x3 (difumina el borde):")
print(mean_result)

print("\nMediana 3x3 (conserva el borde):")
print(median(edge_image))

assert np.allclose(median(edge_image), edge_image)


print("\n=== OPERACIONES EN SECUENCIA ===")

# Apertura aplicada dos veces da el mismo resultado (idempotencia).
once = opening(noisy)
twice = opening(once)

assert np.allclose(once, twice)

# Cierre aplicado dos veces también.
assert np.allclose(closing(closing(holed)), closing(holed))

print("Apertura y cierre son idempotentes:")
print("aplicarlas dos veces da el mismo resultado.")


print("\nTodas las pruebas pasaron.")
