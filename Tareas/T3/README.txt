CC5213 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA - 2020-2
FACULTAD DE CIENCIAS FISICAS Y MATEMÁTICAS, UNIVERSIDAD DE CHILE
Profesor: Juan Manuel Barrios
Estudiante: Matías Vergara Silva
Fecha: 17 de Noviembre de 2020

1. OBJETIVO DEL PROGRRAMA

El objetivo de este programa es detectar avisos de comerciales en televisión, entregando tanto el nombre del comercial
correspndiente como el instante en el que comienza y por cuanto se extiende. Para ello el programa requiere recibir la
ruta a una carpeta con audios de emisión televisiva y a una carpeta con audios de avisos comerciales. El programa
crea los descriptores correspondientes utilizando MFCC. Los descriptores se comparan buscando similitudes y finalmente
el resultado se plasma en un archivo de detecciones.

2. DEPENDENCIAS

El programa se implementa en Python 3.9. Se requiere contar con las siguientes librerias:

- [numpy]   (https://numpy.org):
            Para el manejo eficiente de arreglos guardados como archivo binario. Versión 1.19.2.
            Instalación mediante `pip install numpy==1.19.2`.

- [librosa] (https://librosa.org/doc/latest/index.html):
            Para el análisis de audio. Versión 0.8.0.
            Instalación mediante `pip install librosa==0.8.0`.

- [ffmpeg]  (https://github.com/kkroening/ffmpeg-python):
            Herramienta de línea de comando para convertir entre distintos formatos de audio y video, capturar y
            codificar fuentes en tiempo real, entre otras funciones.
            Instalación mediante `pip install ffmpeg-python`.
            Se debe también descargar e instalar el ejecutable desde https://ffmpeg.org/download.html

- [pydub]   (https://pypi.org/project/pydub/):
            Para la manipulación de audios. Utilizado en este proyecto como una herramienta opcional (desactivada por
            defecto) para dividir audios.
            Instalación mediante `pip install pydub==0.24.1`.

- [time]    (https://docs.python.org/3/library/time.html):
            Para acceder al tiempo de ejecución. Parte de las librerías estándar de Python 3.

- [sys]     (https://docs.python.org/3/library/sys.html):
            Para manejar argumentos entregados al llamar al programa. Parte de las librerías estándar de Python 3.

- [os]      (https://docs.python.org/3/library/os.html):
            Para acceder a directorios y sus archivos. Parte de las librerías estándar de Python 3.

- [re]      (https://docs.python.org/3/library/re.html):
            Para manejar expresiones regulares, necesario para ordenar directorio. Parte de las librerías estándar de
            Python 3.

- [pathlib]      (https://docs.python.org/3/library/pathlib.html):
            Para manipular rutas a directorios y archivos. Parte de las librerías estándar de Python 3.

También se debe contar con el script 'utilsRIM_T3.py' en la misma carpeta donde se esté trabajando. Este script contiene
una serie de funciones sencillas pero esenciales para el correcto funcionamiento del programa. 3 de ellas son de autoría
externa:

- convertir_a_wav: string string -> None
  Autor: Profesor Juan Manuel Barrios.
  Fuente: CC5213 - Anexo 7.1. - Código Python
  Extraído el 26 de Octubre de 2020.
  Recibe la ruta a un audio en formato mp3 y la ruta donde se quiera guardar como wav. Realiza el proceso de conversión
  y grabado.

- create_audio_descriptors: string int -> double[][]
  Autor: Profesor Juan Manuel Barrios.
  Fuente: CC5213 - Anexo 7.1. - Código Python
  Extraído el 26 de Octubre de 2020.
  Recibe la ruta a un archivo de audio en formato wav y un entero correspondiente a un factor de escala.
  Calcula y retorna el descriptor MFCC de dicho audio, con 80 características, una cantidad de muestras por ventana
  equivalente al sample rate dividido por el factor, y un hop length del mismo valor. El resultado es una matriz de
  dimensiones (n_caracteristicas, n_ventanas).

- sorted_alphanumeric: list(str)
  Autor: user136036
  Fuente: https://stackoverflow.com/questions/4813061/non-alphanumeric-list-order-from-os-listdir
  Extraído el 28 de Octubre de 2020.
  Para ordenar alfanuméricamente una lista de archivos obtenida mediante listdir.
  Necesario para normalizar el orden en que se reciben los archivos desde el sistema operativo.

El resto de las funciones son de autoría propia, están debidamente documentadas y son de complejidad baja. Se presentan
de esta forma para evitar repetición de código (pues se utilizan frecuentemente) y dar más modularidad al mismo.


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
    guardar los resultados de procesar los audios. El programa abre el directorio e itera sobre cada audio que encuentra
    realizando el siguiente proceso:

        - Convertir el audio a wav
        - Calcular el descriptor MFCC con los parámetros antes mencionados (Véase línea 65)
        - Escribir el descriptor en forma binaria en la ruta indicada, por medio de un write-append.

    Una vez que se procesan todos los frames de un audio, se escribe el nombre del mismo y el número de descriptores
    creados en un archivo adicional, de nombre n_descriptores.txt, en la misma ruta de los descriptores.

    Cabe mencionar que al inicio del script se define una variable esencial para el funcionamiento eficaz y eficiente
    del programa, de nombre factor, correspondiente al factor de escala que se utiliza para calcular la cantidad de
    muestras por ventana en el MFCC (Véase línea 65). Se recomienda dejar este valor en 2. Aumentarlo extenderá
    ampliamente el tiempo de ejecución superando fácilmente la hora. Disminuirlo puede reducir la efectividad del
    programa.


    4.2. tarea2-busqueda.py

    Este script recibe como parámetros las rutas hacia las carpetas de descriptores de tv y comerciales, ademas de una
    ruta hacia donde se quiera guardar su resultado (un archivo de texto indicando los pares de descriptores en
    tv-comerciales que se identifiquen como 'similares').  Su funcionamiento es el siguiente:

        - Para cada descriptor de audio de televisión, iniciar las primeras 4 distancias minimas como la distancia
          con valores elevados (2^32) y los indices de los descriptores correspondientes en 0.

        - Iterar sobre cada uno de los descriptores de comercial actualizando las distancias mínimas. Si se encuentra un
          nuevo mínimo, los valores en las distancias se desplazan una posición (perdiéndose aquellos de la cuarta
          distanca mínima) y el nuevo valor se guarda en la primera distancia mínima. Lo mismo con los índices asociados.

        - Una vez que se terminan de recorrer todos los descriptores de comerciales, escribir en el archivo objetivo
          una linea con el nombre del descriptor de televisión correspondiente, el instante de la emisión que describe
          y los 4 descriptores de comerciales más cercanos, junto al valor de la distancia encontrada, separando mediante
          tabulaciones:

            capitulo_de_tv tiempo_en_capitulo_de_tv comercial_1  distancia_1 comercial_2 distancia_2 ... distancia_4


    4.3. tarea2-deteccion.py

    Este script recibe como parámetros la ruta hacia el resultado de aplicar el script anterior y una ruta hacia donde
    se quiera guardar el resultado final. Su funcionamiento se basa en estudiar el archivo de similares buscando
    identificar las comparaciones que corresponden efectivamente a comerciales mediante las siguientes condiciones:

        - Un comercial corresponde a una secuencia considerablemente larga de descriptores de televisión apareadas con
          descriptores consecutivos de un mismo comercial. Cada secuencia tiene sin embargo una cantidad de ''permisos''
          para romper la condición antes de considerarse como descartable: la variable "gap_max".

        - Una vez que un comercial se considera como 'descartable' pues excedió el maximo gap permitido, se evalua
          su escritura o descarte como sigue:
            - Si el largo de la secuencia (su número de 'votos') es mayor a un largo mínimo determinado (variable
              min_votos) y el valor de confianza del emparejamiento (calculado como numero de descriptores encontrados
              dividido en el numero de descriptores totales del comercial) es mayor a un valor mínimo exigido, declarado
              en la variable confianza_min, entonces se escribe en el archivo de detecciones una línea como la siguiente:

                    capitulo_de_tv  comercial_emparejado tiempo_de_inicio_en_tv duracion    confianza

            - En caso contrario, la secuencia se descarta y se continua iterando.

    Lo anterior se realiza mediante un diccionario, en donde las llaves corresponden al nombre del comercial y
    los valores a una 3-tupla que almacena el número actual de votos, un boolean indicando la presencia o ausencia del
    comercial en la fila actual de 'similares' y un contador del gap mantenido hasta ese momento. El gap se reinicia una
    vez que se retoma la secuencia.

    Cabe mencionar que las variables anteriormente mencionadas se declaran al inicio del script, en la sección
    "VARIABLES DETERMINANTES EN LA EFICIENCIA Y EFICACIA DEL PROGRAMA".

    Hacia el final del script hay una serie de instrucciones opcionales, cuyo objetivo es fusionar duplicados en el
    archivo de duplicados inicial. Esta parte solo se activa si la variable 'pasadas' (declarada junto a las anteriores)
    es mayor a 0. Su funcionamiento es básicamente dar una cantidad 'pasadas' de revisiones al archivo, fusionando líneas
    consecutivas de un mismo comercial bajo la condición de que alguno de ellos presente un valor de confianza por debajo
    del umbral definido como min_cfza_pasadas. Se recomienda dejar el valor de pasadas en 1 si el umbral
    inicial (confianza_min) es menor a 0.4, en 2 si es menor a 0.25 y en 0 si es mayor a 0.4.


5. ANÁLISIS DE RESULTADOS Y POSIBLES MEJORAS

    5.1. Eficacia

    Se obtienen los siguientes resultados para cada dataset:

    Indicador                   |       dataset_a       |        dataset_b      |    dataset_c   |     Promedio
    ------------------------------------------------------------------------------------------------------------------
    detecciones totales         |         18/24         |         43/48        |       25/31     |      80,64%
    ------------------------------------------------------------------------------------------------------------------
    detecciones correctas       |         17/18         |         42/43        |       25/25     |       97,37%
    ------------------------------------------------------------------------------------------------------------------
    Precision                   |         0.944         |         1.000*       |       1.000     |       0.981
    ------------------------------------------------------------------------------------------------------------------
    Recall                      |         0.708         |         0.875        |       0.806     |       0,796
    ------------------------------------------------------------------------------------------------------------------
    F1                          |         0.810         |         0.933        |       0.893     |       0,879
    ------------------------------------------------------------------------------------------------------------------
    IoU promedio                |         72.4%         |         80.4%        |       77.9%     |       76,9%
    ------------------------------------------------------------------------------------------------------------------
    *: El programa de evaluación seleccionó 42 detecciones con un score umbral 0.375. Por ello la precisión es 1 aún
     cuando hay una detección incorrecta, pues esta quedó fuera de los seleccionados.

    El programa presenta valores de precisión considerablemente altos: casi todas las detecciones que encuentra son
    verdaderas, dando origen a una precisión promedio de 0,98. Sin embargo, no logra encontrar todas: en promedio,
    encuentra el 80,64% de los comerciales.

    5.2. Tiempo de ejecución

    El tiempo de ejecución requerido para cada uno de los datasets y scripts es el siguiente:

    Script                              |       dataset_a       |       dataset_b       |       dataset_c
    --------------------------------------------------------------------------------------------------------
    tarea2-descriptores.py - television |     261.94 segundos   |     203.87 segundos   |    255.99 segundos
    --------------------------------------------------------------------------------------------------------
    tarea2-descriptores.py - comercials |     18.46  segundos   |     3.26   segundos   |    19.86  segundos
    --------------------------------------------------------------------------------------------------------
    tarea2-busqueda.py                  |    2729.67 segundos   |    2777.75 segundos   |    2792.67segundos
    --------------------------------------------------------------------------------------------------------
    tarea2-deteccion.py                 |     0.429  segundos   |     0.078  segundos   |    0.444  segundos
    --------------------------------------------------------------------------------------------------------

    Se observa que el proceso más lento es el de tarea2-busqueda.py, que ronda los 50 minutos. Esto no es de extrañar:
    en la búsqueda de similitudes se compara cada descriptor de video de televisión con cada uno de los descriptores de
    de comerciales, lo que constituye una operación de orden O(mn) con m el número de descriptores de
    televisión y m el número de descriptores de comerciales. Si además notamos que por cada descriptor de televisión
    hay 4 descriptores de comerciales asociados (por los 4 vecinos más cercanos), el orden resulta ser O(4mn).
    Una forma de reducir el tiempo de búsqueda es considerando solo los 3 primeros vecinos más cercanos. Sin embargo,
    esto puede influir negativamente en la eficacia del programa, y no se recomienda pues el tiempo utilizado con 4
    vecinos sigue siendo menor a la mitad del tiempo total de emisión en cada uno de los datasets de prueba.

    En caso de requerir trabajar con emisiones más largas, se recomienda hacer uso de la función 'split_wav' en
    el script utilsRIMT3 para primero dividir la emisión en distintos segmentos, pues de otra forma puede presentar
    problemas de memoria.

6. FUENTES

La implementación se basa en el material entregado  por el profesor Juan Manuel Barrios  en el curso CC5213 -
Recuperación de Información Multimedia de la Universidad de Chile, en su versión 2020-2. El profesor entregó además
un código fuente base para los tres módulos anteriormente descritos, con la recepción de parámetros ya implementada.

En particular fue de gran utilidad el script 'Anexo 7.1. - Código Python', en donde el profesor entregó las principales
funciones necesarias para procesar audio, presentadas anteriormente (Véase línea 58). Estas son el motor principal del
programa, por lo que se agradece enormemente.

También se utilizó una función auxiliar extraída de Stack Overflow, de nombre sorted_alphanumeric (Véase linea 74).
Agradecimientos al usuario 'user136036' por compartir sus conocimientos de forma pública. Fue de gran utilidad.


Matías Vergara Silva.
Facultad de Ciencias Físicas y Matemáticas,
Universidad de Chile.
Noviembre, 2020.

