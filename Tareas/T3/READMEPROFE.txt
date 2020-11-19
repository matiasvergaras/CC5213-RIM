CC5213 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
Profesor: Juan Manuel Barrios
Fecha: 30 de octubre de 2020


1. Descargar todos los archivos de esta carpeta.

2. Para verificar que ha descargado bien y que tiene el mismo archivo escribir el comando:
        md5sum -c MD5SUM

  Para Windows existen múltiples implementacionesde md5sum. El port de la versión de GNU se
  puede descargar desde: http://gnuwin32.sourceforge.net/packages/coreutils.htm

3. Leer el enunciado de la tarea.

4. Para resolver la tarea debe escribir tres programas:

    1)tarea3-busqueda.py     [ruta-videos]          [ruta-descriptores]
    2)tarea3-descriptores.py [ruta-descriptores-tv] [ruta-descriptores-comerciales] [archivo-similares]
    3)tarea3-deteccion.py    [archivo-similares]    [archivo-detecciones]

 Se incluye una base para estos tres archivos. En el enunciado se describe lo que debe hacer cada uno.

5. Para evaluar su tarea debe ejecutar el comando:

    python tarea3-evaluar.py   dataset_a   work_a
    python tarea3-evaluar.py   dataset_b   work_b
    python tarea3-evaluar.py   dataset_c   work_c

6. El evaluador ejecutará la tarea de la siguiente forma para cada dataset:

    python tarea3-descriptores.py  dataset_a/television            work_a/descriptores_television
    python tarea3-descriptores.py  dataset_a/comerciales           work_a/descriptores_comerciales
    python tarea3-busqueda.py      work_a/descriptores_television  work_a/descriptores_comerciales  work_a/similares.txt
    python tarea3-deteccion.py     work_b/similares.txt            work_b/detecciones.txt

En la consola entregará la cantidad de respuestas correctas e incorrectas al comparar "work_a/detecciones.txt" con "dataset_a/gt.txt"
