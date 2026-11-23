# TP 6 - Segmentación

Trabajo práctico de Introducción al Procesamiento Digital de Imágenes.

Consigna: actividad práctica del Slice 7 (diapositiva 17), con los cambios
dichos en clase: se hacen los puntos 1 y 2, y en el punto 2 se agrega
Teh-Chin. Marching squares también está implementado.

Segmentar es separar la imagen en partes: en este TP, separar la **figura**
del **fondo** (punto 1) y encontrar dónde está el **borde** entre ellos
(punto 2).

Todo se calcula sobre la luminancia `Y` (espacio YIQ, valores en [0, 1]),
igual que en los TPs anteriores.

## Funcionalidades

### Punto 1: binarización

-   50 % negro / 50 % blanco
-   Dos modas y distancia mínima
-   Otsu

### Punto 2: bordes

-   Laplaciano v4 y v8
-   Borde interior, borde exterior y gradiente morfológico
-   Marching squares de orden 0 y de orden 1
-   Teh-Chin (contorno y puntos dominantes)

### Extra

-   Mediana 3x3, para sacar el ruido sal y pimienta antes de buscar bordes.

## Punto 1: binarización

Binarizar es pasar la imagen a solo dos valores: negro (fondo) y blanco
(figura). Los tres métodos usan la misma regla, la función `threshold()`:

    blanco si f(x, y) > T
    negro  si f(x, y) <= T

Lo único que cambia entre los métodos es **cómo se elige el umbral T**. La
aplicación muestra en la barra de estado el umbral que usó cada método, para
poder compararlos.

### 50 % negro / 50 % blanco (`binarize_50`)

Se pone en blanco la mitad más clara de los pixels, con el método del
"porcentaje fijo" (`level_50`):

1.  Se suma el histograma desde el nivel más oscuro hasta juntar el 50 % de
    los pixels.
2.  El umbral `k` es el nivel del último bin sumado: los niveles `<= k` van a
    negro y el resto a blanco.

Con un solo umbral el 50 % puede no ser exacto: si muchos pixels tienen el
mismo nivel, quedan todos del mismo lado. Por eso la aplicación informa el
porcentaje de blancos que quedó. En las imágenes (a) y (b) da 50,0 % y
49,4 %.

No mira la forma del histograma: si la figura ocupa el 25 % de la imagen,
igual pinta de blanco el 50 %.

### Dos modas y distancia mínima (`binarize_modes`)

La **moda** es el valor más frecuente: la columna más alta del histograma. Cada
pixel va a la clase de la moda que tiene **más cerca**, y eso es lo mismo que
cortar justo en el medio:

    T = (moda oscura + moda clara) / 2

Para encontrar las dos modas (`find_modes`):

1.  Histograma de 100 columnas de igual ancho. Con columnas anchas, varios
    niveles parecidos se juntan y el ruido no arma modas falsas.
2.  T inicial = luminancia media de la imagen.
3.  Moda oscura = la columna más alta de la parte `<= T`. Moda clara = la
    más alta de la parte `> T`.
4.  Nuevo T = punto medio entre las dos modas. Se repiten 3 y 4 hasta que T
    no cambie.

### Otsu (`otsu`, `binarize_otsu`)

Prueba **todos** los umbrales posibles (k = 0..255) y se queda con el que
mejor separa las dos clases, o sea, el que deja las medias del fondo y de la
figura lo más lejos posible entre sí. Sigue los 7 pasos de la diapositiva:

1.  Histograma normalizado `p_i = n_i / N`.
2.  Sumas acumulativas `P1(k)`: qué proporción de pixels queda en el fondo.
3.  Medias acumulativas `m(k)`.
4.  Media global `mG`.
5.  Varianza entre clases para cada k:
    `σB²(k) = (mG·P1(k) − m(k))² / (P1(k)·(1 − P1(k)))`.
6.  `k*` es el k que maximiza `σB²` (si hay empate, se promedian).
7.  Separabilidad `μ* = σB²(k*) / σG²`, entre 0 y 1.

La **separabilidad** dice qué tan bien funciona: cerca de 1 el histograma
tiene dos montañas bien separadas; cerca de 0, no hay dos clases claras.

Como Otsu elige `k*` sobre el histograma (niveles enteros 0..255), la
binarización también compara en niveles (`threshold_levels`): los pixels de
nivel `k*` o menor quedan en negro (clase C1 = [0, k*]).

## Punto 2: bordes

### Laplaciano (`laplacian_edges`)

Es la convolución del TP4 con los kernels Laplacianos v4 y v8. Donde la
imagen es pareja da 0, y donde hay un cambio brusco da valores grandes,
positivos del lado claro del borde y negativos del lado oscuro. Para mostrarlo
se aplica la coerción a [0, 1], igual que en el TP4: lo negativo pasa a 0 y lo
mayor que 1 pasa a 1, así que se ve el lado claro de cada borde.

Responde a cualquier cambio brusco, también al **ruido**: con ruido sal y
pimienta cada pixel ruidoso aparece como un borde. Por eso conviene aplicar
antes la mediana (ver "Aplicación en secuencia").

**Detector de bordes y pasaaltos no son lo mismo.** En la consigna del TP4
eran dos grupos distintos: detectores de bordes (Laplaciano y Sobel) y
pasaaltos con frecuencia de corte 0,2 y 0,4.

-   Un **pasaaltos** se define por las frecuencias que deja pasar: elimina
    las bajas (las zonas parejas) y deja las altas. Su ganancia es cero, así
    que los coeficientes del kernel suman 0.
-   Un **detector de bordes** se define por lo que encuentra: los lugares
    donde la luminancia cambia de golpe. Su resultado se lee como "acá hay un
    borde", no como una imagen filtrada.

El Laplaciano es un pasaaltos (suma 0: en una zona pareja da 0) que se usa
como detector de bordes, y así se usa en este TP. Sobel también detecta
bordes, pero con la primera derivada y en una dirección.

Tampoco hay que confundirlo con el **realce**: sumar a la imagen un poco de
Laplaciano (kernel identidad + 0,2 · Laplaciano). Ese kernel suma 1, así que
conserva la imagen y solo refuerza los bordes.

### Bordes morfológicos

Usan la erosión (mínimo 3x3) y la dilatación (máximo 3x3) del TP5:

-   Borde interior = original − erosión (la última capa de la figura).
-   Borde exterior = dilatación − original (la primera capa del fondo).
-   Gradiente morfológico = dilatación − erosión (los dos juntos).

### Marching squares (`marching_squares`)

Dibuja la línea donde la imagen cruza el umbral T (se usa el de Otsu).

Se recorre la imagen de a **celdas de 2x2 pixels**. Cada una de las 4
esquinas queda arriba o abajo del umbral, así que hay 2⁴ = 16 casos, y para
cada caso hay una tabla (`MS_CASES`) que dice por qué lados de la celda
entra y sale la línea.

Como dice la diapositiva, las 16 posibilidades se resumen en solo **5 casos
y sus rotaciones**. En la tabla se ve: muchos casos son el mismo dibujo
girado, y un caso y su negativo (`15 − caso`) dan el mismo segmento. Los
casos 5 y 10 (esquinas opuestas) son los únicos con dos segmentos.

-   **Orden 0**: la línea corta cada lado justo en la mitad.
-   **Orden 1**: interpolación lineal. Si en una punta del lado vale 0.2, en
    la otra 0.8 y T = 0.35, la línea corta al 25 % del camino. Queda más
    suave.

El resultado se calcula al doble de tamaño, porque la diferencia entre los
dos órdenes es de menos de un pixel. En la ventana la vista previa se achica
y casi no se nota: para verla hay que guardar el resultado ("Guardar
resultado").

### Teh-Chin (`dominant_points`)

Busca las **esquinas** de la figura (puntos dominantes): los puntos donde el
contorno dobla más que en sus vecinos.

En una figura limpia da un polígono de pocos vértices: en un cuadrado sin
ruido encuentra justo las 4 esquinas. **En la imagen (a) no**: el contorno
tiene 864 pixels y da 155 puntos (802 y 144 si antes se aplica la mediana),
uno cada 6 pixels más o menos. El ruido deja escalones de 1 o 2 pixels en el
borde, y para el algoritmo cada escalón es una esquina de verdad. Teh-Chin no
tiene un umbral para decir "esta esquina es demasiado chica": elige solo el
tamaño de la región que mira en cada punto. Por eso, para tener pocos
vértices, hay que limpiar el contorno antes, no subir el corte de −0,99 (ese
corte solo descarta los tramos rectos). Un círculo tampoco tiene esquinas, así
que da muchos puntos repartidos por todo el borde.

1.  Se binariza con Otsu y se limpia con apertura y cierre (TP5), para que
    el ruido no deforme el contorno.
2.  Se toma la figura blanca más grande (`largest_component`).
3.  Se recorre su contorno en orden con el **seguimiento de Moore**
    (`trace_boundary`): desde cada pixel del borde se miran los 8 vecinos en
    sentido horario y se avanza al primero que sea figura. Se usa el
    criterio de parada de Jacob, para no cortar antes de tiempo si la figura
    tiene un "cuello" por el que se pasa dos veces.
4.  Para cada punto del contorno (`teh_chin`):
    -   **Región de soporte**: cuántos vecinos `k` hacia cada lado hay que
        mirar para ver la forma local. Se agranda `k` mientras se cumplan
        las dos condiciones: la cuerda `l` entre los dos extremos sigue
        creciendo, y la relación `d / l` (distancia del punto a la cuerda
        sobre el largo de la cuerda) no baja.
    -   **Significancia**: el coseno del ángulo que forman los dos extremos
        con el punto. Vale −1 en un tramo recto y se acerca a 1 en una
        esquina aguda.
    -   **Supresión de no máximos**: el punto queda solo si es el más
        "esquina" de su región.

La aplicación dibuja el contorno en celeste, el polígono de puntos
dominantes en rojo y cada punto dominante con un círculo amarillo
(`draw_teh_chin`).

## Aplicación en secuencia

El botón "Usar resultado como entrada" copia la imagen procesada en la
entrada, para aplicar otra operación sobre ella. Por ejemplo, con la imagen
con ruido sal y pimienta: **Mediana** → usar resultado como entrada →
**Laplaciano**. El Laplaciano marca mucho menos ruido: en la imagen (a)
aparece el borde del círculo, aunque adentro del cuadrado todavía queda
bastante ruido.

## Interfaz

La aplicación utiliza Tkinter y permite:

-   Cargar una imagen.
-   Visualizar la imagen de entrada y el resultado.
-   Seleccionar y aplicar una operación.
-   Ver en la barra de estado el umbral usado al binarizar.
-   Utilizar el resultado como nueva imagen de entrada.
-   Restaurar la imagen original.
-   Guardar el resultado en formato PNG.

Las funciones de procesamiento se encuentran separadas de la interfaz en el
módulo `utils.py`.

## Para repasar rápido

| Método            | Qué hace                                 | Idea clave                                           |
|-------------------|------------------------------------------|------------------------------------------------------|
| 50 % / 50 %       | Blanco la mitad más clara                | Histograma acumulado hasta 50 %; ignora su forma     |
| Dos modas         | Corta entre los dos picos                | T = (moda oscura + moda clara) / 2                   |
| Otsu              | Prueba todos los k, elige el mejor       | Maximiza la varianza entre clases; μ* mide la calidad |
| Laplaciano        | Segunda derivada por convolución         | Marca bordes y también ruido                         |
| Borde morfológico | Resta erosión/dilatación                 | Interior, exterior o ambos (gradiente)               |
| Marching squares  | Línea del umbral, celda por celda        | 16 casos = 5 + rotaciones; orden 0 = mitad, orden 1 = interpolado |
| Teh-Chin          | Esquinas del contorno                    | Región de soporte + coseno + no máximos              |

Preguntas que conviene tener claras:

-   ¿Por qué 50 % / 50 % puede dar una figura más grande que la real?
    Porque fuerza la mitad en blanco aunque la figura ocupe menos.
-   ¿Cuándo dan parecido "dos modas" y Otsu? Cuando el histograma tiene dos
    montañas bien separadas y de tamaño parecido (separabilidad alta).
-   ¿Por qué aplicar la mediana antes del Laplaciano? Porque el Laplaciano
    amplifica el ruido sal y pimienta y la mediana lo elimina sin
    difuminar los bordes.
-   ¿Qué diferencia hay entre orden 0 y orden 1 en marching squares? Dónde
    se ubica el corte sobre cada lado de la celda: en la mitad o
    interpolado según los valores.

## Tecnologías

-   Python
-   NumPy
-   Pillow
-   Tkinter

## Ejecución

Desde la raíz del repositorio:

``` bash
python tp_6/tp6_pdi.py
```

Si se utiliza el entorno virtual del proyecto:

``` bash
source .venv/bin/activate
python tp_6/tp6_pdi.py
```
