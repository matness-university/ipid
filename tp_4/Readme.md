# TP 4 - Procesamiento por convolución

Trabajo práctico de Introducción al Procesamiento Digital de Imágenes.

El objetivo es aplicar distintos filtros espaciales sobre la luminancia de una
imagen mediante operaciones de convolución.

## Funcionalidades

El programa permite cargar una imagen, convertirla al espacio YIQ y aplicar
los siguientes filtros sobre la componente de luminancia `Y`:

### Filtros pasabajos

-   Plano 3x3
-   Plano 5x5
-   Plano 7x7
-   Bartlett 3x3
-   Bartlett 5x5
-   Bartlett 7x7
-   Gaussiano 5x5
-   Gaussiano 7x7

### Detectores de bordes

-   Laplaciano v4
-   Laplaciano v8
-   Sobel E
-   Sobel NE
-   Sobel N
-   Sobel NW
-   Sobel W
-   Sobel SW
-   Sobel S
-   Sobel SE

### Filtros pasaaltos y pasabanda

-   Pasaaltos con frecuencia de corte 0.2
-   Pasaaltos con frecuencia de corte 0.4
-   Pasabanda 5x5 mediante diferencia de Gaussianas

## Convolución

La imagen RGB se convierte al espacio YIQ utilizando la función:

-   `rgb_to_yiq()`

Los filtros se aplican sobre la componente de luminancia `Y` mediante la
función:

-   `convolution()`

Para realizar la convolución, el kernel se rota 180 grados y se recorre la
imagen aplicándolo sobre cada píxel y su vecindad.

En los bordes de la imagen se utiliza repetición de filas y columnas para
obtener los valores necesarios fuera de los límites de la imagen.

Las funciones de procesamiento y generación de kernels se encuentran
separadas de la interfaz en el módulo `utils.py`.

## Interfaz

La aplicación utiliza Tkinter y permite:

-   Cargar una imagen.
-   Visualizar la imagen de entrada y el resultado.
-   Seleccionar y aplicar un filtro.
-   Utilizar el resultado como nueva imagen de entrada.
-   Restaurar la imagen original.
-   Guardar el resultado en formato PNG.

## Tecnologías

-   Python
-   NumPy
-   Pillow
-   Tkinter

## Ejecución

Desde la raíz del repositorio:

``` bash
python tp_4/tp4_pdi.py
```

Si se utiliza el entorno virtual del proyecto:

``` bash
source .venv/bin/activate
python tp_4/tp4_pdi.py
```