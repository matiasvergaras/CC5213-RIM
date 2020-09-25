**Sintaxis de Markdown**
# Buscador de imágenes derivadas o duplicadas

Tarea 1 CC5213, Recuperación de Información Multimedia 

Profesor: Juan Manuel Barrios (https://juan.cl)

Alumno: Matías Vergara Silva

Fecha de entrega: 28/09/2020

## Objetivo del programa

El objetivo de esta tarea es implementar un **buscador de imágenes derivadas o duplicadas**, que dado un conjunto de imagenes **R** y un conjunto de posibles duplicados **Q**, determine aquellas imágenes **q** en **Q** que corresponden a transformaciones **T** de alguna imagen **r** en **R**:  *q* | *T ( r ) = q*.

Se considera como transformación una función *T* que recibe como entrada una imagen *r* y genera como salida una imagen *q* que es una *edición* de *r*. Una transformación será válida cuando es posible reconocer el contenido de *r* en *q*. 

Entre las ediciones a evaluar, se encuentran: 
- Bajar calidad (Q)
- Recortar una zona (C)
- Insertar texto + color (T)
- Combinación lineal de las anteriores (V)

Se espera que la tarea detecte al menos un 50% de las imágenes correctamente.

## Librerías utilizadas

Entre las librerías a utilizar, se encuentran:
- [time](https://docs.python.org/3/library/time.html): para acceder al tiempo de ejecución. Parte de las librerías estándar de Python.
- [sys](https://docs.python.org/3/library/sys.html): para manejar argumentos entregados al llamar al programa. Parte ed las librerías estándar de Python.
- [os](https://docs.python.org/3/library/os.html): para acceder a directorios y sus archivos. Parte de las librerías estándar de Python.
- [numpy](https://numpy.org): para el manejo eficiente de arreglos de gran tamaño,
- [scipy](https://www.scipy.org): para el calculo de distancias entre vectores. Versión 1.1.0, instalación mediante `pip install scipy`.
- [cv2](https://pypi.org/project/opencv-python/): para manipular imágenes computacionalmente. Versión 4.4.0.42, instalación mediante `pip install opencv-contrib-python` en MacOS, `pip install opencv-python`en Windows.  

## Implementación 

La tarea se implementa en Python 3.7, a través de 3 módulos. 

### `utils_RIM.py`

Contiene la función `abrir_imagen(filename)` (de autoría del profesor Juan Manuel Barrios) que abre una imagen `"filename"` en memoria mediante el uso de `cv2.imread` (verificando que la imagen se cargue correctamente) y la función `matriz_intensidades(dir_img, tamaño, dir_to_save="")`, que implementa y retorna los descriptores "vector de intensidad" para cada una de las imagenes en `dir_img`.

La función `matriz_intensidades` trabaja de la siguiente manera:

1.  Abre una a una las imágenes del directorio especificado mediante una iteración sobre todos los archivos de la carpeta, verificando en primer lugar  que la extensión del archivo sea `.jpg` (si no, ignora el archivo).

2.  Luego abre la imagen con la función `abrir_imagen`, aplica un resize de tamaño `tamaño` mediante `cv2.resize`, convierte la imagen a escala de grises mediante `cv2.cvtColor` y convierte la imagen a un vector 1D (*flatten*) mediante numpy.

3. A continuación, ingresa dicho vector como fila a una matriz previamente creada de dimensiones `imagenes x tamaño` y guarda también el nombre de la imagen procesada en un vector.

4.   En caso de que se especifique una dirección de guardado `dir_to_save`, la información procesada es almacenada en archivos de texto (matriz de vectores *flatten* en `dataImgToVector.txt` y vector de nombres en `namesImg.txt`) dentro de la dirección entregada (que debe existir previamente). 

5. Finalmente, se retornan la matriz de descriptores y el vector de nombres.

### `tarea1-procesar.py`

Este script debe ser llamado junto al nombre de la carpeta en donde se guardan las imágenes *R* `dir_imgR` y el nombre de carpeta donde se desea guardar la descripción de estas, `dir_datos`. La primera carpeta debe existir previamente, y ambas deben ser accesibles desde la ubicación del programa.

El script toma el tiempo de ejecución, verifica que la cantidad de argumentos entregada sea la correcta y, en tal caso, llama a la función `matriz_intensidades` de `utils_RIM.py`con dirección de guardado `dir_datos` y `tamaño=30` (este parámetro tiene una incidencia directa en el tiempo de ejecución y los resultados, pues determina el tamaño de la descripción de las imágenes). 

### `tarea1-buscar.py`

Este script funciona tras ejecutar previamente `tarea1-procesar.py dir_imgR dir_datos`, y debe ser llamado junto al nombre de la carpeta en donde se guardan las imágenes *Q* `dir_imgQ`, el nombre de carpeta donde está almacenada la información de *R* `dir_datos` y el nombre que se quiere dar al archivo de resultados, `resultados`. 

El script toma el tiempo de ejecución, carga la información en `dir_datos` en memoria y aplica la función `matriz_intensidades` de `utilsRIM.py` con las imágenes de `dir_imgQ` y el mismo `tamaño` de las imágenes en la matriz de `dir_datos`. Se calcula la distancia entre la matriz resultante y el previamente procesado usando la funcion `cdist`de `scipy`, con métrica `minkowski`. Luego se hace una pasada sobre la matriz de distancias resultante buscando la imagen con menor distancia a cada imagen de `Q`,  cuidando de mantener la información del indice en el cual se encuentra el mínimo pues se utiliza para rescatar el nombre de la imagen duplicada desde el vector de nombres.

Tras cada emparejamiento se escribe una línea en el archivo de nombre `resultados`, según el formato siguiente: 

`nombre_imagen_q`   `nombre_imagen_r`   `distancia_entre_q_y_r`. 

Los nombres se obtienen fácilmente mediante el uso de los indices del ciclo sobre la matriz, pues se encuentran en la misma posición que las imágenes en sus archivos correspondientes.

## Descriptor: Vector de Intensidades
El descriptor implementado corresponde al **Vector de Intensidades**, uno de los descriptores más simples entre los estudiados en el curso. La descripción que entrega se basa en guardar la intensidad de cada pixel en escala de grises (0-255) en un arreglo de 1 dimensión, denominado *flatten*.  Luego se puede comparar con otras imágenes mediante la similitud entre arreglos. 

Si bien este descriptor es rápido y de fácil implementación, pierde mucha información al convertir una imagen (una matriz) en un vector, en especial aquella sobre la presencia de objetos en la imagen (pues no hace ningún tipo de evaluación de bordes o gradientes).


## Resultados 

Se evalúan los resultados obtenidos mediante el script `tarea1-evaluar.py`, entregado por el profesor y de su autoría. Se utilizan dos datasets de imágenes: `dataset_a` y `dataset_b`, disponibles en el [Drive de la tarea](https://drive.google.com/drive/folders/1fYORDbjEalNU8fcvVaLNCtr6-7IQ9a4R). Los resultados son los siguientes.

### Dataset A
```bash
Resultado logrado = 793 correctas de 1600 (50%)
  Resultados por tipo de query
    Q-CALIDAD     = 400 (100%)
    C-CROP        =  66 (16%)
    T-TEXTO+COLOR = 310 (78%)
    V-VARIOS      =  17 (4%)
```

### Dataset B
```bash
Resultado logrado = 804 correctas de 1600 (50%)
  Resultados por tipo de query
    Q-CALIDAD     = 400 (100%)
    C-CROP        =  60 (15%)
    T-TEXTO+COLOR = 327 (82%)
    V-VARIOS      =  17 (4%)
```

## Análisis de Resultados y posibles mejoras
Se observa una porcentaje de éxito aceptable según lo esperado (50%), debido principalmente a un buen comportamiento con respecto a imágenes cuya transformación corresponde a una disminución de calidad (`Q-CALIDAD`) o a la adición de un texto y/o cambio en los colores (`T-TEXTO+COLOR`).  

Por otro lado, el programa falla ampliamente en la tarea de identificar imágenes recortadas (`C-CROP`, con un 15-16% de logro) e imágenes que han sufrido varias transformaciones (`V-VARIOS`, con un 4% de logro) sobre los sets de prueba presentados. 

**El bajo porcentaje de logro con respecto a la transformación de recortado** es comprensible si se tiene en consideración el hecho de que todas las imágenes están siendo adaptadas a un mismo tamaño, con lo que se pierde la posibilidad de verificar si una imagen corresponde a un trozo de otra. Sin embargo, este redimensionamiento es fundamental para la comparación vector a vector. 

**Una posible forma de obtener mejores resultados** sería utilizar un descriptor en base a histogramas de orientación del gradiente (HOG) o a histograma de bordes (EHD), guardando en primer lugar un descriptor global para cada imagen de Q (por si fuera un recorte) y luego calculando descriptores por zonas tanto para las imágenes en Q y R. De esta forma, para cada imagen en Q habría que comparar su descriptor global contra cada zona de las imágenes en R, guardar las distancias, proceder a comparar los descriptores por zonas entre sí, guardar estas nuevas distancias, y luego escoger el mínimo entre ambos sets de distancia. 

La implementación anteriormente propuesta podría mostrar una robustez mucho mayor frente a recortes (y a `V` también, probablemente). Sin embargo, resultaría mucho más lenta de ejecutar y compleja de programar (se intentó por horas, sin buen resultado).

**El bajo porcentaje de logro con respecto a la transformación `V-VARIAS`**se arrastra del mal resultado ante `C-CROP`, dado que `VARIAS` es una combinación lineal de las otras operaciones (incluyendo `CROP`).

## Uso
```bash
python tarea1-procesar.py [dir_imágenes_R] [datos_R]
#se crean los archivos en el directorio datos_R. Debe existir previamente.
python tarea1-buscar.py [dir_imágenes_Q] [datos_R] [resultados.txt]
#se crea el archivo resultados.txt y se guardan en él los resultados.
```

## Fuentes
Toda la implementación se basa en el material entregado  por el profesor **Juan Manuel Barrios**  en el curso **CC5213 - Recuperación de Información Multimedia** de la Universidad de Chile, en su versión 2020-2. 