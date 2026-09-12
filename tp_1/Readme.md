# TP 1 - Procesamiento Digital de Imágenes

Aplicación desarrollada con Python y Tkinter para la materia
Introducción al Procesamiento Digital de Imágenes.

## Objetivo

Manipular independientemente la luminancia y la saturación de una imagen
mediante la conversión entre los espacios de color RGB y YIQ.

La aplicación utiliza como base la interfaz desarrollada en el TP 0.

## Funcionalidades

-   Cargar y visualizar una imagen.
-   Convertir una imagen de RGB a YIQ.
-   Modificar la luminancia mediante el coeficiente `a`.
-   Modificar la saturación mediante el coeficiente `b`.
-   Convertir el resultado nuevamente de YIQ a RGB.
-   Mostrar la imagen de entrada y la imagen resultado.
-   Pasar la imagen resultado como nueva entrada.
-   Restaurar la imagen original.
-   Guardar la imagen resultado en formato PNG.
-   Visualizar el histograma de intensidades.

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
python tp1_pdi.py
```

## Uso

1.  Abrir una imagen.
2.  Ingresar un valor para luminancia `a`.
3.  Ingresar un valor para saturación `b`.
4.  Presionar `Aplicar luminancia y saturación`.
