# TP 0 - Procesamiento Digital de Imágenes

Aplicación desarrollada con Python y Tkinter para la materia
Introducción al Procesamiento Digital de Imágenes.

## Objetivo

Desarrollar una interfaz básica para cargar, visualizar y procesar
imágenes, manteniendo una imagen de entrada y una imagen resultado.

## Funcionalidades

-   Cargar y visualizar una imagen.
-   Mostrar una imagen de entrada y una imagen resultado.
-   Aplicar operaciones básicas de procesamiento:
    -   Escala de grises.
    -   Visualización del canal rojo.
    -   Visualización del canal verde.
    -   Visualización del canal azul.
-   Pasar la imagen resultado como nueva entrada.
-   Restaurar la imagen original en la entrada.
-   Guardar la imagen resultado en formato PNG.
-   Visualizar el histograma de intensidades de la imagen de entrada o
    resultado.

## Tecnologías

-   Python
-   Tkinter
-   NumPy
-   Pillow
-   Matplotlib

## Instalación

``` bash
pip install numpy pillow matplotlib
```

## Ejecución

``` bash
python tp0_pdi.py
```

## Uso

1.  Abrir una imagen.
2.  Seleccionar una operación de procesamiento.
3.  Presionar `Aplicar operación`.
4.  El resultado se visualizará junto a la imagen de entrada.
5.  Opcionalmente, utilizar el resultado como nueva entrada, restaurar
    la imagen original, visualizar su histograma o guardar el resultado.
