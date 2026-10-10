import numpy as np

from utils import (
    band_pass_kernel,
    convolution,
    flat_kernel,
    bartlett_kernel,
    gaussian_kernel,
    laplacian_kernel_v4,
    laplacian_kernel_v8,
    sobel_kernel,
    high_pass_kernel,
)

image = np.array([[0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [0.5, 0.5, 0.5]])


print("=== PASABAJOS PLANO 3x3 ===")

kernel = flat_kernel(3)

print("Kernel:")
print(kernel)

result = convolution(image, kernel)

print("Resultado:")
print(result)


print("\n=== BARTLETT 3x3 ===")

kernel = bartlett_kernel(3)

print("Kernel:")
print(kernel)

print("Suma:", kernel.sum())

result = convolution(image, kernel)

print("Resultado:")
print(result)

print("\n=== COMPARACIÓN 3x3 ===")

image_detail = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])

flat = flat_kernel(3)
bartlett = bartlett_kernel(3)

result_flat = convolution(image_detail, flat)

result_bartlett = convolution(image_detail, bartlett)

print("Imagen:")
print(image_detail)

print("\nPlano:")
print(result_flat)

print("\nBartlett:")
print(result_bartlett)

for size in [3, 5, 7]:
    kernel = bartlett_kernel(size)
    print(f"\nBartlett {size}x{size}:")
    print(kernel)
    print("Suma:", kernel.sum())


print("\n=== GAUSSIANO ===")

for size in [5, 7]:
    kernel = gaussian_kernel(size)

    print(f"\nGaussiano {size}x{size}:")
    print(kernel)
    print("Suma:", kernel.sum())


print("\n=== LAPLACIANO ===")

laplacian_v4 = laplacian_kernel_v4()
laplacian_v8 = laplacian_kernel_v8()

print("\nLaplaciano v4:")
print(laplacian_v4)
print("Suma:", laplacian_v4.sum())

print("\nLaplaciano v8:")
print(laplacian_v8)
print("Suma:", laplacian_v8.sum())

print("\nResultado v4 sobre imagen constante:")
print(convolution(image, laplacian_v4))

print("\nResultado v8 sobre imagen constante:")
print(convolution(image, laplacian_v8))

print("\n=== LAPLACIANO SOBRE UN BORDE ===")

edge_image = np.array(
    [
        [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
        [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
        [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
        [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
        [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
    ]
)

print("\nImagen:")
print(edge_image)

result_v4 = convolution(edge_image, laplacian_v4)

result_v8 = convolution(edge_image, laplacian_v8)

print("\nLaplaciano v4:")
print(result_v4)

print("\nLaplaciano v8:")
print(result_v8)

print("\n=== PRUEBA CONVOLUCION DIRECCIONAL ===")

directional_kernel = np.array([[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]])

directional_result = convolution(edge_image, directional_kernel)

print("\nKernel entregado:")
print(directional_kernel)

print("\nKernel realmente aplicado:")
print(np.rot90(directional_kernel, 2))

print("\nResultado:")
print(directional_result)

print("\n=== SOBEL 8 ORIENTACIONES ===")

directions = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]

for direction in directions:
    kernel = sobel_kernel(direction)

    print(f"\nSobel {direction}:")
    print(kernel)
    print("Suma:", kernel.sum())

    result = convolution(edge_image, kernel)

    print("Resultado:")
    print(result)


print("\n=== SOBEL SOBRE BORDE HORIZONTAL ===")

horizontal_edge = np.array(
    [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0, 1.0],
    ]
)

for direction in ["E", "N", "W", "S"]:
    kernel = sobel_kernel(direction)

    result = convolution(horizontal_edge, kernel)

    print(f"\nSobel {direction}:")
    print(result)


print("\n--- HIGH PASS FILTERS ---")

for cutoff in [0.2, 0.4]:
    kernel = high_pass_kernel(cutoff)

    print(f"\nHigh pass fc = {cutoff}")
    print(kernel)
    print("Sum:", kernel.sum())

    constant_image = np.ones((7, 7)) * 0.5

    result = convolution(constant_image, kernel)

    print("Constant image result:")
    print(np.round(result, 6))


print("\n=== PRUEBA FRECUENCIAL PASAALTOS ===")

width = 32
height = 32

x = np.arange(width)

low_frequency = 0.2 * np.sin(2 * np.pi * 0.1 * x)

high_frequency = 0.2 * np.sin(2 * np.pi * 0.3 * x)

signal = 0.5 + low_frequency + high_frequency

image = np.tile(signal, (height, 1))

for cutoff in [0.2, 0.4]:
    kernel = high_pass_kernel(cutoff)

    result = convolution(image, kernel)

    print(f"\nHigh pass fc = {cutoff}")
    print(np.round(result[height // 2], 3))

print("\n=== PASABANDA DoG ===")

kernel = band_pass_kernel()

print("Kernel:")
print(kernel)

print("Shape:", kernel.shape)
print("Suma:", kernel.sum())

constant_image = np.full((5, 5), 0.5, dtype=float)

result = convolution(constant_image, kernel)

print("Imagen constante:")
print(np.round(result, 6))
