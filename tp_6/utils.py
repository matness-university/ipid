"""
Funciones de Procesamiento Digital de Imágenes.

Este módulo contiene las funciones utilizadas por el TP6
para realizar segmentación. Todas trabajan sobre la
luminancia Y (espacio YIQ) con valores en [0, 1], igual
que en los TPs anteriores.

Punto 1 (binarización):
    binarize_50, binarize_modes, binarize_otsu.

Punto 2 (bordes):
    laplacian_edges, inner_border, outer_border,
    morphological_gradient, marching_squares y
    dominant_points (Teh-Chin).
"""

import numpy as np

from PIL import Image, ImageDraw

RGB_TO_YIQ = np.array(
    [
        [0.299, 0.587, 0.114],
        [0.595716, -0.274453, -0.321263],
        [0.211456, -0.522591, 0.311135],
    ]
)


def rgb_to_yiq(image):
    return image @ RGB_TO_YIQ.T


def load_luminance(pil_image):
    """
    Imagen de PIL -> luminancia Y en [0, 1].

    Es lo mismo que hace la interfaz al abrir una imagen:
    RGB normalizado entre 0 y 1, paso a YIQ y me quedo con Y.
    """

    rgb = np.array(pil_image.convert("RGB")) / 255.0

    return np.clip(rgb_to_yiq(rgb)[:, :, 0], 0, 1)


# ============================================================
# HISTOGRAMA Y UMBRAL
# ============================================================

# Cantidad de niveles de gris (0 a 255), como en el TP3.
LEVELS = 256


def to_levels(image):
    """
    Pasa la luminancia en [0, 1] a niveles enteros 0..255.

    El histograma necesita niveles enteros para poder
    contar cuántos pixels hay de cada nivel.
    """

    levels = np.round(image * (LEVELS - 1))

    return np.clip(levels, 0, LEVELS - 1).astype(int)


def histogram(image):
    """
    Histograma: cantidad de pixels n_i de cada nivel i.
    """

    return np.bincount(to_levels(image).ravel(), minlength=LEVELS)


def threshold(image, t):
    """
    Umbral global (Slice 7, p. 5):

        1 (blanco) si f(x, y) > T
        0 (negro)  si f(x, y) <= T

    Los tres métodos del punto 1 usan esta regla. Lo único
    que cambia entre ellos es cómo se elige el valor de T.
    """

    return (image > t).astype(float)


def threshold_levels(image, k):
    """
    La misma regla, pero comparando en niveles enteros 0..255:

        1 (blanco) si nivel > k
        0 (negro)  si nivel <= k

    Hace falta para Otsu y para el 50 %, que eligen k mirando
    el histograma, que cuenta niveles enteros. Un pixel con Y = 0.3735 cae en
    el nivel 95 (0.3735 * 255 = 95.2 -> 95), así que si k* = 95
    Otsu lo cuenta en la clase C1 = [0, k*] (fondo). Pero
    0.3735 > 95 / 255 = 0.3725, así que threshold(image, k*/255)
    lo pintaría de blanco. Comparando en niveles no pasa.
    """

    return (to_levels(image) > k).astype(float)


# ============================================================
# PUNTO 1: BINARIZACIÓN 50 % / 50 %
# ============================================================


def level_50(image):
    """
    Umbral para que la mitad de los pixels quede en negro.

    Es el método del "porcentaje fijo" de Russ (cap. 7): se
    suma el histograma desde el nivel más oscuro hasta llegar
    a la fracción buscada (acá, el 50 % de los pixels). El
    umbral es el nivel del último bin que se sumó.

    Devuelve ese nivel k (0..255).
    """

    # Proporción acumulada de pixels con nivel <= k.
    cumulative = np.cumsum(histogram(image)) / image.size

    # Primer nivel en el que ya se juntó al menos el 50 %.
    return int(np.argmax(cumulative >= 0.5))


def binarize_50(image):
    """
    Binarización con 50 % de pixels negros y 50 % blancos.

    Negro: niveles <= k (la mitad más oscura).
    Blanco: niveles > k.

    Con un solo umbral el 50 % puede no ser exacto: si muchos
    pixels tienen el mismo nivel, ese nivel entero queda del
    mismo lado. Por ejemplo, en un cuadrado claro sobre fondo
    oscuro donde el 75 % de los pixels es fondo (todos del
    mismo valor), solo queda 25 % en blanco.
    """

    return threshold_levels(image, level_50(image))


# ============================================================
# PUNTO 1: DOS MODAS Y DISTANCIA MÍNIMA
# ============================================================


# Columnas del histograma para buscar las modas. Con 256
# niveles el ruido sal y pimienta (pixels en 0 y en 1) arma
# "modas" falsas en los extremos. Con columnas más anchas cada
# columna junta varios niveles parecidos, y la moda de verdad
# se destaca. Se usan 100, como el código de Otsu de la cátedra
# (03_Otsu1.txt, bins = 100).
MODE_COLUMNS = 100


def column_histogram(image, columns=MODE_COLUMNS):
    """
    Histograma de columnas de igual ancho (Slice 4, p. 5):
    la columna j cuenta los pixels con Y en [j/columns, (j+1)/columns).
    El 1.0 va a la última columna.

    Devuelve la cantidad de pixels de cada columna y el centro
    de cada columna (como luminancia en [0, 1]).
    """

    column = np.clip((image * columns).astype(int), 0, columns - 1)

    counts = np.bincount(column.ravel(), minlength=columns)

    centers = (np.arange(columns) + 0.5) / columns

    return counts, centers


def find_modes(image, columns=MODE_COLUMNS):
    """
    Busca la moda oscura y la moda clara del histograma.

    La moda de un grupo de pixels es su valor más frecuente:
    la columna más alta del histograma. Para tener dos modas
    hay que separar primero los pixels en oscuros y claros, y
    para eso hace falta un umbral. Se resuelve iterando:

    1) T inicial = luminancia media de la imagen.
    2) Moda oscura = la columna más alta con centro <= T.
       Moda clara  = la columna más alta con centro >  T.
    3) Nuevo T a mitad de camino entre las modas (Slice 7, p. 7).
    4) Repetir 2 y 3 hasta que T no cambie.

    Es el umbral global básico de Gonzalez y Woods (sec. 10.3),
    que hace lo mismo con la media de cada grupo. Acá se usa la
    moda, que es lo que pide la consigna.

    Devuelve las dos modas como luminancia en [0, 1].
    """

    counts, centers = column_histogram(image, columns)

    t = image.mean()

    dark = light = t

    # Normalmente termina en pocas vueltas; el límite es por
    # las dudas, para que nunca quede en un bucle infinito.
    for _ in range(100):
        dark_side = centers <= t

        # Si de un lado no hay ningún pixel (por ejemplo, una
        # imagen de un solo gris), no hay dos modas que buscar.
        if counts[dark_side].sum() == 0 or counts[~dark_side].sum() == 0:
            break

        dark = centers[dark_side][np.argmax(counts[dark_side])]
        light = centers[~dark_side][np.argmax(counts[~dark_side])]

        new_t = (dark + light) / 2

        if new_t == t:
            break

        t = new_t

    return float(dark), float(light)


def modes_threshold(image):
    """
    Umbral por distancia mínima a las dos modas.

    Cada pixel va a la clase de la moda que tiene más cerca.
    Eso es lo mismo que cortar justo a mitad de camino entre
    las dos modas (Slice 7, p. 7):

        T = (moda oscura + moda clara) / 2
    """

    dark, light = find_modes(image)

    return (dark + light) / 2


def binarize_modes(image):
    """
    Binarización por dos modas y distancia mínima.
    """

    return threshold(image, modes_threshold(image))


# ============================================================
# PUNTO 1: OTSU
# ============================================================


def otsu(image):
    """
    Método de Otsu siguiendo los 7 pasos de la diapositiva
    (Otsu, p. 2-7).

    Idea: probar todos los umbrales k posibles y quedarse con
    el que mejor separa las dos clases, es decir, el que hace
    que las medias de fondo y figura queden lo más lejos
    posible entre sí (máxima varianza entre clases).

    Devuelve (k*, mu*):
        k*  -> el umbral en niveles 0..255.
        mu* -> la separabilidad, entre 0 y 1. Cuanto más
               cerca de 1, más bimodal es el histograma y
               mejor funciona la binarización.

    Con T = k*, la clase C1 = [0, k*] es el fondo y la
    clase C2 = [k* + 1, L - 1] es la figura.
    """

    n = histogram(image)
    i = np.arange(LEVELS)

    # 1) Histograma normalizado: p_i = n_i / N.
    p = n / n.sum()

    # 2) Sumas acumulativas P1(k): proporción de pixels
    #    que caen en la clase C1 = [0, k].
    P1 = np.cumsum(p)

    # 3) Medias acumulativas m(k).
    m = np.cumsum(i * p)

    # 4) Media global de toda la imagen.
    mG = m[-1]

    # 5) Varianza entre clases para cada k:
    #
    #        sigma_B^2(k) = (mG * P1(k) - m(k))^2
    #                       ---------------------
    #                       P1(k) * (1 - P1(k))
    #
    #    Donde P1 vale 0 o 1, una de las clases está vacía
    #    (se dividiría por cero), así que ahí se deja 0.
    denominator = P1 * (1 - P1)

    non_empty = denominator > 1e-12

    sigma_b = np.zeros(LEVELS)

    sigma_b[non_empty] = (mG * P1[non_empty] - m[non_empty]) ** 2 / denominator[
        non_empty
    ]

    # 6) k* es el k que maximiza sigma_B^2.
    #    Si hay varios máximos iguales, se promedian.
    best = np.flatnonzero(np.isclose(sigma_b, sigma_b.max()))

    k_star = int(round(best.mean()))

    # 7) Separabilidad: mu* = sigma_B^2(k*) / sigma_G^2,
    #    donde sigma_G^2 es la varianza global.
    sigma_g = np.sum((i - mG) ** 2 * p)

    mu = sigma_b[k_star] / sigma_g if sigma_g > 0 else 0.0

    return k_star, mu


def otsu_threshold(image):
    """
    Umbral de Otsu como luminancia en [0, 1]: T = k* / (L - 1).

    Lo usa marching squares, que necesita un T continuo para
    interpolar (orden 1). Para binarizar se usa binarize_otsu,
    que compara en niveles (ver threshold_levels).
    """

    k_star, _ = otsu(image)

    return k_star / (LEVELS - 1)


def binarize_otsu(image):
    """
    Binarización de Otsu: C1 = [0, k*] negro (fondo) y
    C2 = [k* + 1, L - 1] blanco (figura).
    """

    k_star, _ = otsu(image)

    return threshold_levels(image, k_star)


# ============================================================
# PUNTO 2: BORDES POR LAPLACIANO (convolución del TP4)
# ============================================================

LAPLACIAN_V4 = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=float)

LAPLACIAN_V8 = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=float)


def convolution(image, kernel):
    """
    Convolución con repetición de bordes, igual que en el TP4.
    """

    size = kernel.shape[0]
    pad = size // 2

    # Repetimos los valores de los bordes de la imagen.
    padded_image = np.pad(image, pad, mode="edge")

    # En la convolución el kernel se rota 180 grados.
    rotated_kernel = np.rot90(kernel, 2)

    result = np.zeros_like(image, dtype=float)

    # Recorremos cada pixel de la imagen.
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            window = padded_image[i : i + size, j : j + size]

            result[i, j] = np.sum(window * rotated_kernel)

    return result


def laplacian_edges(image, kernel=LAPLACIAN_V4):
    """
    Bordes por Laplaciano.

    Donde la luminancia es pareja el Laplaciano da 0, y en
    los cambios bruscos (bordes, pero también ruido) da
    valores grandes, positivos de un lado del borde y
    negativos del otro.

    Para verlo se aplica la coerción a [0, 1], como en el TP4
    (Slice 5, p. 26): lo negativo pasa a 0 y lo mayor que 1
    pasa a 1. Queda marcado el lado claro de cada borde.
    """

    return np.clip(convolution(image, kernel), 0.0, 1.0)


# ============================================================
# PUNTO 2: BORDES MORFOLÓGICOS (vecindad 3x3 del TP5)
# ============================================================


def neighborhood_filter(image, function, size=3):
    """
    Recorre la imagen y, para cada pixel, aplica una función
    sobre los valores de su vecindad 3x3 (igual que en el TP5).
    """

    pad = size // 2

    # Repetimos los valores de los bordes de la imagen.
    padded_image = np.pad(image, pad, mode="edge")

    result = np.zeros_like(image, dtype=float)

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            window = padded_image[i : i + size, j : j + size]

            result[i, j] = function(window)

    return result


def erosion(image):
    """
    Erosión: mínimo de la vecindad 3x3.
    """

    return neighborhood_filter(image, np.min)


def dilation(image):
    """
    Dilatación: máximo de la vecindad 3x3.
    """

    return neighborhood_filter(image, np.max)


def median(image):
    """
    Mediana de la vecindad 3x3. Elimina el ruido sal y
    pimienta sin difuminar los bordes.
    """

    return neighborhood_filter(image, np.median)


def opening(image):
    """
    Apertura: erosión seguida por dilatación.

    Elimina detalles claros de menor tamaño que el
    elemento estructurante.
    """

    return dilation(erosion(image))


def closing(image):
    """
    Cierre: dilatación seguida por erosión.

    Rellena detalles oscuros (huecos) de menor tamaño
    que el elemento estructurante.
    """

    return erosion(dilation(image))


def inner_border(image):
    """
    Borde interior: original menos erosión.
    """

    return image - erosion(image)


def outer_border(image):
    """
    Borde exterior: dilatación menos original.
    """

    return dilation(image) - image


def morphological_gradient(image):
    """
    Gradiente morfológico: dilatación menos erosión.

    Es la suma del borde exterior y el borde interior.
    """

    return dilation(image) - erosion(image)


# ============================================================
# PUNTO 2: MARCHING SQUARES
# ============================================================
#
# Se recorre la imagen de a "celdas" de 2x2 pixels. Cada
# esquina de la celda queda arriba (1) o abajo (0) del umbral.
# Con 4 esquinas hay 2^4 = 16 casos posibles, y para cada caso
# ya se sabe por dónde pasa el contorno dentro de la celda.
#
# El número de caso se arma con 4 bits:
#
#     arriba-izq = 8      arriba-der = 4
#     abajo-izq  = 1      abajo-der  = 2
#
# Aristas de la celda:
#
#              0 (arriba)
#            +-----------+
#   3 (izq)  |           |  1 (der)
#            +-----------+
#              2 (abajo)
#
# Cada caso dice qué par de aristas une cada segmento.
# Un caso y su "negativo" (15 - caso) dan el mismo segmento.
# Los casos 5 y 10 (esquinas opuestas) son ambiguos y llevan
# dos segmentos.

MS_CASES = {
    0: [],
    15: [],
    1: [(3, 2)],
    14: [(3, 2)],
    2: [(2, 1)],
    13: [(2, 1)],
    3: [(3, 1)],
    12: [(3, 1)],
    4: [(0, 1)],
    11: [(0, 1)],
    6: [(0, 2)],
    9: [(0, 2)],
    7: [(3, 0)],
    8: [(3, 0)],
    5: [(3, 0), (2, 1)],
    10: [(0, 1), (3, 2)],
}


def edge_point(edge, i, j, corners, t, order):
    """
    Punto (fila, columna) donde el contorno cruza una arista
    de la celda cuya esquina superior izquierda es (i, j).

    Orden 0: el corte se pone en la mitad de la arista.
    Orden 1: interpolación lineal. Si en un extremo vale `a`
             y en el otro `b`, el corte está en la fracción
             (t - a) / (b - a) del camino. Así el contorno
             queda más suave.
    """

    tl, tr, br, bl = corners

    # Para cada arista: sus dos extremos y el valor en cada uno.
    ends = {
        0: ((i, j), (i, j + 1), tl, tr),
        1: ((i, j + 1), (i + 1, j + 1), tr, br),
        2: ((i + 1, j), (i + 1, j + 1), bl, br),
        3: ((i, j), (i + 1, j), tl, bl),
    }

    (r0, c0), (r1, c1), a, b = ends[edge]

    fraction = 0.5

    if order == 1 and a != b:
        fraction = (t - a) / (b - a)

    row = r0 + fraction * (r1 - r0)
    col = c0 + fraction * (c1 - c0)

    return (float(row), float(col))


def marching_squares(image, t, order=0):
    """
    Contorno de la curva de nivel image = t.

    Devuelve una lista de segmentos ((fila0, col0), (fila1, col1))
    en coordenadas de pixel.
    """

    segments = []

    above = image > t

    for i in range(image.shape[0] - 1):
        for j in range(image.shape[1] - 1):
            case = (
                8 * above[i, j]
                + 4 * above[i, j + 1]
                + 2 * above[i + 1, j + 1]
                + 1 * above[i + 1, j]
            )

            corners = (
                image[i, j],
                image[i, j + 1],
                image[i + 1, j + 1],
                image[i + 1, j],
            )

            for e0, e1 in MS_CASES[int(case)]:
                p0 = edge_point(e0, i, j, corners, t, order)
                p1 = edge_point(e1, i, j, corners, t, order)

                segments.append((p0, p1))

    return segments


def draw_segments(shape, segments, scale=3):
    """
    Dibuja los segmentos en blanco sobre una imagen negra
    agrandada `scale` veces (si no, las líneas de orden 1 no
    se distinguen de las de orden 0).
    """

    h, w = shape

    canvas = np.zeros((h * scale, w * scale))

    for (r0, c0), (r1, c1) in segments:
        # Dos puntos por pixel de largo, para que la línea
        # no quede cortada.
        points = int(max(abs(r1 - r0), abs(c1 - c0)) * scale * 2) + 2

        rr = np.linspace(r0, r1, points) * scale
        cc = np.linspace(c0, c1, points) * scale

        rr = np.clip(np.round(rr).astype(int), 0, h * scale - 1)
        cc = np.clip(np.round(cc).astype(int), 0, w * scale - 1)

        canvas[rr, cc] = 1.0

    return canvas


# ============================================================
# PUNTO 2: CONTORNO Y PUNTOS DOMINANTES DE TEH-CHIN
# ============================================================

# Los 8 vecinos de un pixel, numerados en sentido horario:
#
#     0 1 2
#     7 · 3
#     6 5 4
#
# La dirección opuesta a d es (d + 4) % 8.
NEIGHBORS_8 = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
    (1, 0),
    (1, -1),
    (0, -1),
]


def largest_component(binary):
    """
    Devuelve una máscara con la componente conexa más grande
    (8-vecindad) de una imagen binaria, es decir, la figura
    blanca más grande.
    """

    h, w = binary.shape

    visited = np.zeros((h, w), dtype=bool)

    largest = []

    for start_i in range(h):
        for start_j in range(w):
            if not binary[start_i, start_j] or visited[start_i, start_j]:
                continue

            # "Pintamos" la figura desde este pixel: se visitan
            # sus vecinos, los vecinos de sus vecinos, etc.
            component = []
            pending = [(start_i, start_j)]
            visited[start_i, start_j] = True

            while pending:
                i, j = pending.pop()
                component.append((i, j))

                for di, dj in NEIGHBORS_8:
                    ni, nj = i + di, j + dj

                    inside = 0 <= ni < h and 0 <= nj < w

                    if inside and binary[ni, nj] and not visited[ni, nj]:
                        visited[ni, nj] = True
                        pending.append((ni, nj))

            if len(component) > len(largest):
                largest = component

    mask = np.zeros((h, w), dtype=bool)

    for i, j in largest:
        mask[i, j] = True

    return mask


def trace_boundary(mask):
    """
    Seguimiento del borde de Moore: devuelve la lista ordenada
    de pixels del contorno exterior de la figura (una cadena
    cerrada), en sentido horario.

    Desde cada pixel del borde se miran sus 8 vecinos en
    sentido horario, empezando al lado del pixel desde donde
    se llegó, y se avanza al primero que sea figura.

    Criterio de parada de Jacob: no alcanza con volver al pixel
    inicial, porque si el inicial es un "cuello" (une dos
    partes de la figura) se pasa por él dos veces. Se termina
    cuando, estando en el inicial, el próximo paso repite el
    primer paso del recorrido.

    Si no hay figura, devuelve una lista vacía.
    """

    if not mask.any():
        return []

    # Agregamos un marco de fondo para no salirnos de la imagen.
    h, w = mask.shape
    padded = np.zeros((h + 2, w + 2), dtype=bool)
    padded[1:-1, 1:-1] = mask

    # El inicial es el primer pixel de la figura en orden de
    # lectura, así que a su izquierda (dirección 7) seguro hay
    # fondo: hacemos de cuenta que entramos desde ahí.
    start = tuple(int(v) for v in np.argwhere(padded)[0])
    current = start
    came_from = 7
    first_step = None
    contour = [start]

    while True:
        # Recorremos los 8 vecinos en sentido horario, empezando
        # por el siguiente a la dirección desde donde se llegó.
        next_pixel = None

        for step in range(8):
            d = (came_from + 1 + step) % 8

            ni = current[0] + NEIGHBORS_8[d][0]
            nj = current[1] + NEIGHBORS_8[d][1]

            if padded[ni, nj]:
                next_pixel = (ni, nj)
                next_came_from = (d + 4) % 8
                break

        # Pixel aislado: no tiene vecinos.
        if next_pixel is None:
            break

        # Criterio de Jacob.
        if current == start and next_pixel == first_step:
            break

        if first_step is None:
            first_step = next_pixel

        current = next_pixel
        came_from = next_came_from
        contour.append(current)

    # El último paso vuelve al inicial, que ya está al principio.
    if len(contour) > 1 and contour[-1] == start:
        contour.pop()

    # Quitamos el marco: volvemos a las coordenadas originales.
    return [(i - 1, j - 1) for i, j in contour]


def chord(pts, i, k):
    """
    Cuerda entre p(i - k) y p(i + k).

    Devuelve su largo l y la distancia d (con signo) del
    punto p(i) a la cuerda. El signo indica de qué lado de
    la cuerda está el punto (esquina hacia afuera o hacia
    adentro).
    """

    n = len(pts)

    a = pts[(i - k) % n]
    b = pts[(i + k) % n]
    p = pts[i]

    ab = b - a

    length = np.linalg.norm(ab)

    if length == 0:
        return 0.0, 0.0

    dist = (ab[0] * (p[1] - a[1]) - ab[1] * (p[0] - a[0])) / length

    return length, dist


def teh_chin(contour):
    """
    Puntos dominantes de Teh y Chin (1989) sobre una curva
    cerrada. Devuelve los índices (en el contorno) de los
    puntos dominantes, que son las "esquinas" de la figura.

    1) Región de soporte k_i de cada punto: cuántos vecinos
       hacia cada lado hay que mirar. Se agranda k mientras
       la cuerda l = |p(i-k) p(i+k)| siga creciendo y la
       relación d / l (distancia del punto a la cuerda sobre
       su largo) no empiece a bajar.

    2) Medida de significancia: k-coseno del ángulo en p_i
       con k = k_i. Vale -1 en un tramo recto (ángulo de 180°)
       y se acerca a 1 cuanto más aguda es la esquina.

    3) Supresión de no máximos: p_i queda solo si su
       significancia es la mayor dentro de su región de
       soporte (|i - j| <= k_i / 2).
    """

    n = len(contour)

    # Con menos de 3 puntos no hay ángulos que medir.
    if n < 3:
        return []

    pts = np.array(contour, dtype=float)

    # 1) Región de soporte.
    support = np.ones(n, dtype=int)

    for i in range(n):
        k = 1

        while k + 1 < n // 2:
            length_k, dist_k = chord(pts, i, k)
            length_next, dist_next = chord(pts, i, k + 1)

            # La cuerda dejó de crecer.
            if length_k == 0 or length_k >= length_next:
                break

            # La relación d / l dejó de crecer (en valor absoluto).
            if dist_k > 0 and dist_k / length_k >= dist_next / length_next:
                break

            if dist_k < 0 and dist_k / length_k <= dist_next / length_next:
                break

            k += 1

        support[i] = k

    # 2) Significancia: coseno del ángulo entre los vectores
    #    p(i-k) - p(i) y p(i+k) - p(i).
    significance = np.full(n, -1.0)

    for i in range(n):
        k = support[i]

        a = pts[(i - k) % n] - pts[i]
        b = pts[(i + k) % n] - pts[i]

        norms = np.linalg.norm(a) * np.linalg.norm(b)

        if norms > 0:
            significance[i] = np.dot(a, b) / norms

    # 3) Supresión de no máximos. Un coseno cercano a -1 es un
    #    tramo recto, así que no se toma como esquina.
    dominant = []

    for i in range(n):
        half = max(1, support[i] // 2)

        window = [significance[(i + d) % n] for d in range(-half, half + 1)]

        if significance[i] >= max(window) and significance[i] > -0.99:
            dominant.append(i)

    return dominant


def dominant_points(image):
    """
    Teh-Chin sobre una imagen de luminancia:

    1) Binariza con Otsu y limpia con apertura y cierre (TP5),
       para que el ruido pegado al borde no deforme el contorno.
    2) Sigue el contorno de la figura más grande.
    3) Calcula sus puntos dominantes.

    Devuelve (contorno, índices de los puntos dominantes).
    Si no hay ninguna figura, las dos listas quedan vacías.
    """

    binary = binarize_otsu(image)

    binary = closing(opening(binary))

    figure = largest_component(binary > 0.5)

    contour = trace_boundary(figure)

    return contour, teh_chin(contour)


def draw_teh_chin(image, contour, dominant, scale=1):
    """
    Dibuja el resultado de Teh-Chin sobre la imagen en gris
    agrandada `scale` veces:

        - contorno en celeste,
        - polígono de puntos dominantes en rojo,
        - cada punto dominante con un círculo amarillo.

    Devuelve una imagen RGB con valores en [0, 1].
    """

    gray = (np.clip(image, 0, 1) * 255).astype(np.uint8)

    canvas = Image.fromarray(np.stack([gray, gray, gray], axis=2))

    if scale != 1:
        canvas = canvas.resize((canvas.width * scale, canvas.height * scale), Image.NEAREST)

    draw = ImageDraw.Draw(canvas)

    # El contorno está en (fila, columna), pero PIL dibuja en
    # (x, y) = (columna, fila). Se apunta al centro del pixel
    # agrandado.
    points = [(c * scale + scale // 2, r * scale + scale // 2) for r, c in contour]

    corners = [points[i] for i in dominant]

    # Se repite el primer punto al final para cerrar la curva.
    if len(points) > 1:
        draw.line(points + [points[0]], fill=(0, 160, 255), width=1)

    if len(corners) > 1:
        draw.line(corners + [corners[0]], fill=(255, 60, 60), width=2)

    for x, y in corners:
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), outline=(255, 220, 0), width=2)

    return np.array(canvas) / 255.0
