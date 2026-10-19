# TP 5 - Procesamiento morfológico

Trabajo práctico de Introducción al Procesamiento Digital de Imágenes.

El objetivo es aplicar operaciones de morfología en niveles de gris sobre la
luminancia de una imagen, utilizando un elemento estructurante de 3x3.

## Funcionalidades

El programa permite cargar una imagen, convertirla al espacio YIQ y aplicar
las siguientes operaciones sobre la componente de luminancia `Y`:

### Operaciones básicas

-   Erosión (mínimo valor de luminancia de la vecindad)
-   Dilatación (máximo valor de luminancia de la vecindad)

### Operaciones combinadas

-   Apertura (erosión seguida por dilatación)
-   Cierre (dilatación seguida por erosión)
-   Borde exterior (dilatación menos original)
-   Borde interior (original menos erosión)
-   Gradiente morfológico (dilatación menos erosión)

### Filtro no lineal

-   Mediana (mediana de los 9 valores de la vecindad)

## Morfología en niveles de gris

La imagen RGB se convierte al espacio YIQ utilizando la función:

-   `rgb_to_yiq()`

Las operaciones se realizan mediante la función:

-   `neighborhood_filter()`

La función recorre cada pixel de la imagen y toma los 9 valores de su
vecindad 3x3, del mismo modo que la convolución del TP4. Sobre esa vecindad
se obtiene el mínimo (erosión), el máximo (dilatación) o la mediana.

A diferencia de la convolución, estas operaciones no son lineales: no se
multiplica por un kernel, sino que se elige un valor de la vecindad.

En los bordes de la imagen se utiliza repetición de filas y columnas para
obtener los valores necesarios fuera de los límites de la imagen, igual que
en el TP4.

Las funciones de procesamiento se encuentran separadas de la interfaz en el
módulo `utils.py`.

## Aplicación en secuencia

En morfología es común combinar dos o más operaciones. Para eso, el botón
"Usar resultado como entrada" copia la imagen procesada en la imagen de
entrada, y permite aplicar otra operación sobre ella.

## Interfaz

La aplicación utiliza Tkinter y permite:

-   Cargar una imagen.
-   Visualizar la imagen de entrada y el resultado.
-   Seleccionar y aplicar una operación morfológica.
-   Utilizar el resultado como nueva imagen de entrada.
-   Restaurar la imagen original.
-   Guardar el resultado en formato PNG.

## Pruebas

El archivo `test.py` verifica las operaciones sobre imágenes pequeñas
(un punto, un cuadrado, una imagen constante, un borde y ruido sal y
pimienta).

``` bash
python tp_5/test.py
```

## Tecnologías

-   Python
-   NumPy
-   Pillow
-   Tkinter

## Ejecución

Desde la raíz del repositorio:

``` bash
python tp_5/tp5_pdi.py
```

Si se utiliza el entorno virtual del proyecto:

``` bash
source .venv/bin/activate
python tp_5/tp5_pdi.py
```
