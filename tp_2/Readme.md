# TP 2 - Aritmética de píxeles

Trabajo práctico de Introducción al Procesamiento Digital de Imágenes.

El objetivo es implementar operaciones aritméticas entre dos imágenes,
trabajando tanto en el espacio RGB como en el espacio YIQ.

## Funcionalidades

El programa permite cargar dos imágenes y aplicar las siguientes
operaciones:

### Operaciones en RGB

-   Suma clampeada
-   Suma promediada
-   Resta clampeada
-   Resta promediada
-   Resta con valor absoluto
-   Producto
-   Cociente

### Operaciones en YIQ

-   Suma clampeada
-   Suma promediada
-   Resta clampeada
-   Resta promediada

### Operaciones condicionales

-   If-lighter
-   If-darker

En las operaciones `if-lighter` e `if-darker` se compara la luminancia
`Y` de ambas imágenes y se conserva el píxel completo correspondiente a
la imagen seleccionada.

## Espacio YIQ

Para las operaciones realizadas en YIQ, las imágenes RGB se convierten
utilizando las funciones:

-   `rgb_to_yiq()`
-   `yiq_to_rgb()`

Las operaciones se realizan sobre las componentes YIQ y el resultado se
convierte nuevamente a RGB para su visualización.

## Interfaz

La aplicación utiliza Tkinter y permite:

-   Cargar una imagen A.
-   Cargar una imagen B.
-   Visualizar ambas imágenes y el resultado.
-   Seleccionar y aplicar una operación.
-   Utilizar el resultado como nueva imagen de entrada.
-   Restaurar la imagen original.
-   Guardar el resultado en formato PNG.
-   Visualizar histogramas.
-   Modificar luminancia y saturación.

## Tecnologías

-   Python
-   NumPy
-   Pillow
-   Tkinter
-   Matplotlib

## Ejecución

Desde la raíz del repositorio:

``` bash
python tp_2/tp2_pdi.py
```

Si se utiliza el entorno virtual del proyecto:

``` bash
source .venv/bin/activate
python tp_2/tp2_pdi.py
```