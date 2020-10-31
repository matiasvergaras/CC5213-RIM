CC5213 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA - 2020-2
FACULTAD DE CIENCIAS FISICAS Y MATEMÁTICAS, UNIVERSIDAD DE CHILE
Profesor: Juan Manuel Barrios
Estudiante: Matías Vergara Silva
Fecha: 14 de octubre de 2020

1. OBJETIVO DEL PROGRRAMA

El objetivo de este programa es detectar avisos de comerciales en televisión, entregando tanto el nombre del comercial
correspndiente como el instante en el que comienza y por cuanto se extiende. Para ello el programa requiere recibir la
ruta a una carpeta con videos de emisión televisiva y a una carpeta con avisos comerciales.

2. DEPENDENCIAS

El programa requiere contar con las siguientes librerias:

- [numpy]   (https://numpy.org):
            Para el manejo eficiente de arreglos guardados como archivo binario. Versión 1.19.2.
            Instalación mediante `pip install numpy==1.19.2`.

- [cv2]     (https://pypi.org/project/opencv-python/):
            Para manipular imágenes computacionalmente. Versión 4.4.0.44.
            Istalación mediante `pip install opencv-contrib-python==4.4.0.44` en MacOS,
            `pip install opencv-python==4.4.0.44`en Windows.

- [time]    (https://docs.python.org/3/library/time.html):
            Para acceder al tiempo de ejecución. Parte de las librerías estándar de Python.

- [sys]     (https://docs.python.org/3/library/sys.html):
            Para manejar argumentos entregados al llamar al programa. Parte de las librerías estándar de Python.

- [os]      (https://docs.python.org/3/library/os.html):
            Para acceder a directorios y sus archivos. Parte de las librerías estándar de Python.

También se debe contar con el script 'utilsRIM_T2.py' en la misma carpeta donde se esté trabajando. Este script contiene
3 funciones sencillas pero esenciales para el correcto funcionamiento del programa:

- distancia_manhattan: array[num](vector a) array[num](vector b) -> float (distancia)
  Devuelve la distancia de manhattan entre los vectores a y b

- proporcionFrames: int(n_frames) string -> float (proporcion n_frames/frames_totales)
  Recibe la cantidad de frames encontrados, el nombre del directorio donde buscar descriptores_comerciales
  y entrega un numero entre 0 y 1 representando la magnitud n_frames_encontrados / n_frames_totales_del_comercial

- canny_automatizado: image int(tamaño) double(desviacion) -> image (aplicando canny)
  Aplica el detector de bordes Canny a la imagen entregada, redimensionada a 'tamaño' x 'tamaño',
  Encontrando de forma automática los valores para high_treshold y low_treshold basandose en el promedio y un valor de
  desviación estándar (por defecto 1/3). Se utiliza L2 para encontrar la magnitud del gradiente.

# diferencia_tolerable: num(a) num(b) num(epsilon) -> boolean
# Retorna True si a y b estan a una distancia menor o igual a epsilon, False si no.


3. USO

Sean [ruta-tv] la ruta a la carpeta con videos de emisión televisiva,  [ruta-comerciales] la ruta a la carpeta con
avisos comerciales, [ruta-obj-tv] la ruta hacia donde se quieren guardar los descriptores de emisión televisiva
(debe terminar en un nombre de carpeta no existente, que el programa creará para guardar los datos ahí) y
[ruta-obj-comerc] la ruta hacia donde se quieren guardar los descriptores de avisos comerciales, bajo las mismas
condiciones que la anterior. Para un correcto funcionamiento del programa, este debe ejecutarse de la siguiente forma:

	python tarea2-descriptores.py       [ruta-tv]                            [ruta-obj-tv]
	python tarea2-descriptores.py       [ruta-comeciales]                    [ruta-obj-comerc]
    python tarea2-busqueda.py           [ruta-obj-tv]  [ruta-obj-comerc]     [ruta-obj-similares]
	python tarea2-deteccion.py          [ruta-obj-similares]                 [ruta-obj-detecciones]


Donde [ruta-obj-similares] corresponde a la ruta en donde se quiere guardar el archivo resultante de comparar los
descriptores de televisión con los de avisos comerciales en búsqueda de similares, y [ruta-obj-detecciones] a la ruta
en donde se quiere guardar el resultado final (un documento con los pares segmento_televisión-candidato_a_comercial).

Es fundamental que los comandos se ejecuten en el orden dado, de lo contrario el programa no funcionará. Solo
los primeros dos comandos pueden alternarse, pero ambos deben ser ejecutados antes de continuar con los siguientes.

4. IMPLEMENTACIÓN

El programa se implementa a traves de 3 módulos, cada uno de los cuales implementa una función específica y necesaria
para el módulo siguiente.

    4.1. tarea2-descriptores.py

    Este script recibe dos parámetros: una ruta a un directorio de videos a procesar, y una ruta hacia donde se quiere
    guardar los resultados de procesar los videos. El programa abre el directorio e itera sobre cada video que encuentra
    realizando el siguiente proceso:

        - Tomar un frame del video
        - Redimensionar el frame a 'tamaño'x'tamaño' pixeles
        - Aplicar el descriptor de bordes Canny  al frame, con parámetros low_treshold y high_treshold adaptativos a
          las intensidades del frame
        - Guardar el descriptor en un arreglo
        - Esperar 3 segundos e iterar.

    Una vez que se procesan todos los frames de un video, se escribe el nombre del video y el número de frames procesados
    en un archivo de texto.

    Una vez que se procesan todos los videos, se guarda el arreglo de descriptores como un archivo binario mediante
    numpy.save().

    Cabe destacar que en este script se definen, en las lineas 26 y 27, dos de los parámetros más determinantes en el
    comportamiento del programa: 'segs', el tiempo de muestreo, y 'tamaño', el tamaño de redimensionamiento. Cambiar
    dichos valores puede tener efectos considerablemente adversos - o positivos - en el programa, sin embargo, se
    recomienda mantener los entregados (pues se obtuvieron tras un gran número de pruebas y errores).

    Si bien el redimensionamiento genera una imágen cuadrada (con mismo largo y ancho), es posible obtener una imágen
    en 16:9 agregando el parámetro 'relacion=True' en el llamado a canny_automatizado. Se recomienda, sin embargo,
    mantener la relación de aspecto 1:1 (cuadrada), pues entrega mejores resultados con la configuración por defecto.

    4.2. tarea2-busqueda.py

    Este script recibe como parámetros las rutas hacia las carpetas de descriptores de tv y comerciales, ademas de una
    ruta hacia donde se quiera guardar su resultado (un archivo de texto indicando los pares de descriptores en
    tv-comerciales que se identifiquen como 'similares').  Su funcionamiento es el siguiente:

        - Para cada descriptor de frame de televisión, iniciar la distancia minima como la distancia al primer
          descriptor de frame de comerciales, usando la distancia de Manhattan.

        - Continuar comparando dicha distancia con la distancia 'actual' entre el frame de televisión y el resto de los
          descriptores de frames de comerciales. Si la distancia actual es menor que la distancia retenida hasta ese
          momento, entonces actualizar dicha distancia con este valor inferior, y continuar iterando.

        - Una vez que se terminan de recorrer todos los descriptores de comerciales, escribir en el archivo objetivo
          una linea con el origen de cada frame y el instante al que pertenecen en el video original (tanto de televisión
          como de comercial) y la distancia entre ellos (que es la mínima), separando por tabulaciones cada valor. Esto
          entrega como resultado columnas con el siguiente formato:

                capitulo_de_tv tiempo_en_capitulo_de_tv    comercial  tiempo_en_comercial  distancia


    4.3. tarea2-deteccion.py

    Este script recibe como parámetros la ruta hacia el resultado de aplicar el script anterior y una ruta hacia donde
    se quiera guardar el resultado final. Su funcionamiento se basa en estudiar el archivo de frames similares buscando
    identificar las comparaciones que corresponden efectivamente a comerciales mediante las siguientes condiciones:

        - Un comercial corresponde a una secuencia considerablemente larga de frames de televisión apareadas con
          frames de un mismo comercial. Si una ocurrencia de similares rompe esta condición, entonces se descarta
          la secuencia como comercial y se continua con los similares siguientes.

        - Un comercial que pase la condición anterior debe además avanzar en el tiempo y hacerlo a un paso idéntico al de
          los frames de televisión.  Se permitirá un desfase máximo de 0.5s entre televisión y comercial, dado los
          redondeos realizados en la toma del tiempo de cada frame.


    En relación a la primera condición:
    Dado que el tamaño de redimensionamiento de frames utilizado es considerablemente alto (60x60 px), no se permitirán
    interrupciones (si una secuencia de frames es cortada en un instante por una aparición de un frame de otro comercial,
    se considerará como que el comercial se terminó). Esto puede inducir a duplicados, pero se optó por esta decisión
    debido a que en el caso contrario aumenta la aparición de falsos positivos.

    En relación a la segunda condición:
    Se permitirá que los frames intermedios de un comercial tengan un tiempo mayor O IGUAL a su antecesor, pues
    en la práctica esto amplia considerablemente las detecciones (de 5 a 24 para el dataset a). Sin embargo, la
    condición debe cumplirse como desigualdad estricta entre los frames inicial y final de cada comercial.

    Para cada detección se genera un valor de 'confianza', definido como el número de frames del comercial encontrados
    divididos en el número total de frames procesados para dicho comercial al momento de crear los descriptores.

    A medida que se detectan candidatos a apariciones de comerciales, el programa escribe un archivo con resultados
    preliminares, en donde se encuentran todos los pares identificados pero con una cantidad de duplicados potencialmente
    grande. Luego se realiza un procesamiento final sobre este archivo, reuniendo los duplicados contiguos en una misma
    detección (bajo la condición de que al menos uno de ellos presente un nivel de confianza menor a un mínimo
    determinado) y escribiéndolos en el archivo de resultados final (en la ruta entregada como parámetro).

    Los resultados finales se presentan en el siguiente formato:

               capitulo_de_tv  comercial_emparejado tiempo_de_inicio_en_tv duracion    confianza

    Donde las columnas se separan por tabulaciones.

5. ANÁLISIS DE RESULTADOS Y POSIBLES MEJORAS

    5.1. Eficacia

    Se obtienen los siguientes resultados para cada dataset:

    Indicador                   |       dataset_a       |        dataset_b      |    dataset_c   |     Promedio
    ------------------------------------------------------------------------------------------------------------------
    detecciones totales         |         14/24         |         40/40        |       20/31     |      64,52%
    ------------------------------------------------------------------------------------------------------------------
    detecciones correctas       |         14/14         |         36/40        |       19/20     |       95%
    ------------------------------------------------------------------------------------------------------------------
    Precision                   |         1.000         |         0.900        |       0.950     |       0.95
    ------------------------------------------------------------------------------------------------------------------
    Recall                      |         0.583         |         0.750        |       0.613     |       0,649
    ------------------------------------------------------------------------------------------------------------------
    F1                          |         0.737         |         0.818        |       0.745     |       0,767
    ------------------------------------------------------------------------------------------------------------------
    IoU promedio                |         33.2%         |         34.7%        |       24.5%     |       30,8%
    ------------------------------------------------------------------------------------------------------------------

    El programa presenta valores de precisión considerablemente altos: casi todas las detecciones que encuentra son
    verdaderas, dando origen a una precisión promedio de 0,95. Sin embargo, el programa presenta dificultad para
    identificar la totalidad de los comerciales, lo que se refleja en un Recall promedio de 0,649. Por su parte, el
    F1-Score promedio para los tres datasets evaluados es de 0,767.

    En general consideramos el resultado como bueno, en cuanto creemos que un posible uso que el programa podría tener
    sería el de identificar comerciales para luego borrarlos del video de televisión, a fin de poder ver los capítulos
    sin interrupciones. Si bien no hay duda de que la permanencia de algunos comerciales sería molesto, el problema sería
    aún mayor si un fragmento de televisión es detectado como comercial y por ende eliminado. Pero esto último casi no
    sucedería con nuestro programa, pues la incidencia de falsos positivos es prácticamente nula.

    5.2. Tiempo de ejecución

    El tiempo de ejecución requerido para cada uno de los datasets y scripts es el siguiente:

    Script                              |       dataset_a       |       dataset_b       |       dataset_c
    --------------------------------------------------------------------------------------------------------
    tarea2-descriptores.py - television |     202.59 segundos   |     203.87 segundos   |    208.36 segundos
    --------------------------------------------------------------------------------------------------------
    tarea2-descriptores.py - comercials |     3.15   segundos   |     3.26   segundos   |    3.89   segundos
    --------------------------------------------------------------------------------------------------------
    tarea2-busqueda.py                  |     431.84 segundos   |     401.75 segundos   |    501.06 segundos
    --------------------------------------------------------------------------------------------------------
    tarea2-deteccion.py                 |     0.066  segundos   |     0.078  segundos   |    0.066  segundos
    --------------------------------------------------------------------------------------------------------

    Se observa que el proceso más lento es el de tarea2-busqueda.py. Esto no es de extrañar: en la búsqueda de
    similitudes se compara cada descriptor de frame de video de televisión con cada uno de los descriptores de
    frame de comerciales, lo que constituye una operación de orden O(mn) con m el número de frames del canal de
    televisión dividido en el tiempo de muestreo, y n lo mismo para los comerciales.  Es de esperar que m sea
    mucho más grande que n, por lo cual podemos afirmar que  según el largo de la emisión de televisión, los tiempos
    de procesamiento escalarán rápidamente.

    En caso de requerir trabajar con emisiones más largas, se recomienda buscar nuevos parámetros para 'segs' y
    'tamaño'. Atención: este proceso puede requerir de una gran cantidad de iteraciones antes de obtener buenos
    resultados, y cada iteración a su vez requerirá de una cantidad considerable de tiempo. En este sentido, se
    recomienda seguir los siguientes lineamientos para encontrar buenos parámetros en un tiempo óptimo:
    - Priorizar reducir 'tamaño'. Valor mínimo para resultados aceptables: 25.
    - Si aún no es suficiente, aumentar 'segs'. Valor máximo: la duración del comercial más corto / 2.

6. FUENTES

Toda la implementación se basa en el material entregado  por el profesor Juan Manuel Barrios  en el curso CC5213
- Recuperación de Información Multimedia de la Universidad de Chile, en su versión 2020-2. El profesor entregó además
un código fuente base para los tres módulos anteriormente descritos, con la recepción de parámetros ya implementada.

