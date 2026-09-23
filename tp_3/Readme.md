# TP 3 - Operaciones de luminancia

Trabajo práctico de Introducción al Procesamiento Digital de Imágenes.

El objetivo es aplicar distintas operaciones sobre la luminancia de una
imagen, trabajando en el espacio de color YIQ.

## Funcionalidades

El programa permite cargar una imagen y aplicar los siguientes filtros:

### Operaciones de luminancia

-   Raíz cuadrada
-   Cuadrado
-   Lineal a trozos

Para el filtro lineal a trozos se pueden seleccionar los valores
`Y min` y `Y max` que determinan el intervalo de luminancia a transformar.

## Espacio YIQ

La imagen RGB se convierte al espacio YIQ utilizando las funciones:

-   `rgb_to_yiq()`
-   `yiq_to_rgb()`

Los filtros modifican únicamente la componente de luminancia `Y`,
manteniendo las componentes `I` y `Q` sin cambios.

Las funciones de procesamiento se encuentran separadas de la interfaz
en el módulo `utils.py`.

## Interfaz

La aplicación utiliza Tkinter y permite:

-   Cargar una imagen.
-   Visualizar la imagen de entrada y el resultado.
-   Seleccionar y aplicar un filtro.
-   Configurar `Y min` y `Y max` para el filtro lineal a trozos.
-   Utilizar el resultado como nueva imagen de entrada.
-   Restaurar la imagen original.
-   Guardar el resultado en formato PNG.
-   Visualizar el histograma de luminancia.

## Tecnologías

-   Python
-   NumPy
-   Pillow
-   Tkinter
-   Matplotlib

## Ejecución

Desde la raíz del repositorio:

``` bash
python tp_3/tp3_pdi.py
```

Si se utiliza el entorno virtual del proyecto:

``` bash
source .venv/bin/activate
python tp_3/tp3_pdi.py
```