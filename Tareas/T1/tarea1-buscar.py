# encoding: utf-8
#Autor: Matias Vergara Silva
#Basado en el Material del curso Recuperacion de Informacion Multimedia de la Universidad de Chile,
#Creado por el profesor Juan Barrios https://www.juan.cl

import time
start_time = time.time()
import sys
import numpy as np
import scipy.spatial
import utilsRIM as RIM


#dist_vec_intensidad: string string -> np.array2D, np.array1D, np.array1D
#recibe dos nombres de carpetas. Procesa las de la primera usando un vector de intensidad,
#y carga los datos de la segunda (imagenes). Luego calcula la distancia de minkowski
#entre sus elementos y la retorna junto a los nombres de las imagenes procesadas.
def dist_vec_intensidad(dir_imgQ, datos_R):
    #Cargamos los archivos de imagenes ya procesadas y sus nombres
    imgsProcsR = np.loadtxt(datos_R+'/'+'dataImgToVector.txt')
    nombresImgsProcs = np.loadtxt(datos_R+'/'+'namesImg.txt', dtype=str)
    #Obtenemos la dimensión de resize estudiando las imagenes ya procesadas
    dimension = int(np.sqrt(len(imgsProcsR[0])))
    imgsProcsQ, nombresQ = RIM.vector_intensidad(dir_imgQ, dimension)

    #Calculamos la distancia de minkowski entre las imagenes recien procesadas de Q y los datos previamente procesados
    # en datos_R cada fila  representa los resultados de comparar una imagen de R contra cada una de las imagenes de Q.
    distancia = scipy.spatial.distance.cdist(imgsProcsQ, imgsProcsR, metric='minkowski')
    return distancia, nombresQ, nombresImgsProcs


#comparar: string np.array2D np.array1D np.array1D -> None
#Busca la distancia minima de cada fila en matrizDistancia y escribe el resultado en un archivo de nombre
#nombreArchivo, en el formato "nombreQ + nombreR + valor_distancia. Los nombres se obtienen de nombresQ y nombresR.
def comparar(nombreArchivo, matrizDistancia, nombresQ, nombresR):
    #Abrimos un archivo en formato escritura para guardar los resultados en el formato pedido.
    respuestas = open(nombreArchivo, "w")
    #Iteramos sobre la matriz de distancia:
    #Cada fila nos indica la distancia de una sola imagen en R contra cada imagen de Q
    indiceQ=0
    for fila in matrizDistancia:
        # iniciamos el valor de distancia en el maximo posible en 32 bits
        indiceR = 0
        mindist = 2147483647
        #Cambiamos este valor a medida que aparece un valor de distancia menor (en los elementos de la fila).
        for valorDist in fila:
            if valorDist < mindist:
                mindist = valorDist
                #Guardamos el valor del índice en el momento en que se alcanzó la distancia mínima,
                #pues lo necesitamos para encontrar el nombre de la imagen
                indiceMinimo = indiceR
            indiceR += 1
        #Obtenemos los nombres haciendo uso de que estan en las mismas posiciones que las imagenes,
        #que conocemos pues tenemos los indices del ciclo.
        nombreQ = nombresQ[indiceQ]
        nombreR = nombresR[indiceMinimo]


        #Imponemos que si la distancia es mayor a cierto valor, entonces la imagen no tiene duplicado.
        #if mindist>2300:
        #   nombreQ = "-"
        #Comentamos esta parte pues para el metodo implementado, no mejora los resultados.

        #Escribimos la linea correspondiente en el archivo de respuesta.
        respuestas.write(nombreQ +'\t'+ nombreR + '\t' + str(mindist) + '\n')
        indiceQ += 1

#programa_principal_buscar: None -> None
#Revisa que los argumentos entregados por sys sean los correspondientes y llama
#a las funciones de emparejamiento.
def programa_principal_buscar():
    # Revisamos que la cantidad de argumentos ingresados sea la correcta
    if len(sys.argv) != 4:
        print("Nombre de argumentos:", len(sys.argv) - 1, 'argumentos. ')
        print("Debe llamar a la funcion con 3 argumentos: dir_imagenes_Q, datos_R y resultados.txt")
        sys.exit(1)
    else:
        dir_imgQ = sys.argv[1]
        dir_datosR = sys.argv[2]
        nombreArchivo = sys.argv[3]
        distancia,nombresQ, nombresImgsProcs = dist_vec_intensidad(dir_imgQ, dir_datosR)
        comparar(nombreArchivo, distancia, nombresQ, nombresImgsProcs)

#Ejecución y reloj
programa_principal_buscar()
print("--- Tiempo de emparejamiento: %s segundos ---" % (time.time() - start_time))