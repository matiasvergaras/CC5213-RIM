import sys
import os.path
import time
import numpy as np
import utilsRIM_T2 as utils

# INICIAR CRONÓMETRO para el tiempo de ejecución
tiempo_inicial=time.time()
if len(sys.argv) < 4:
    print("Uso: {} [descriptores_television_dir] [descriptores_comerciales_dir] [archivo-knn]".format(sys.argv[0]))
    sys.exit(1)

# IDENTIFICAR PARÁMETROS
descriptores_television_dir = sys.argv[1]
descriptores_comerciales_dir = sys.argv[2]
similares_file = sys.argv[3]

# REVISION DE EXISTENCIA DE DIRECTORIOS ENTREGADOS
if not os.path.isdir(descriptores_television_dir):
    print("no existe directorio {}".format(descriptores_television_dir))
    sys.exit(1)
if not os.path.isdir(descriptores_comerciales_dir):
    print("no existe directorio {}".format(descriptores_comerciales_dir))
    sys.exit(1)

# ABRIR DESCRIPTORES
descr_comerciales = np.load(descriptores_comerciales_dir + "/descriptores.npy")
descr_television = np.load(descriptores_television_dir + "/descriptores.npy")

# PROCESAMIENTO: SE GUARDA EL FRAME MÁS CERCANO DE 'descr_comerciales' PARA CADA FRAME EN 'descr_television'

# ABRIR INFORMACIONES ADICIONALES A LOS DESCRIPTORES, CREAR ITERABLES
with open(descriptores_television_dir + "/info_descriptores", "r") as info_television:
    iter_television = info_television.read().split('\n')
    with open(descriptores_comerciales_dir + "/info_descriptores", "r") as info_comerciales:
        iter_comerciales = info_comerciales.read().split('\n')

        # ABRIR ARCHIVO DE ESCRITURA 'SIMILARES'
        with open(similares_file, "w") as similares:

            # Para cada descriptor de frame del capítulo de televisión
            for i in range(0, len(descr_television)):

                # Inicializar la distancia como aquella entre el frame de televisión y el primer frame de comercial
                distancia = utils.distancia_manhattan(descr_television[i], descr_comerciales[0])
                indice_similar = 0

                # Para cada comercial, revisar si la distancia se reduce, en cuyo caso, actualizar y guardar el indice
                for j in range(0, len(descr_comerciales)):
                    nueva_distancia = utils.distancia_manhattan(descr_television[i], descr_comerciales[j])
                    if nueva_distancia < distancia:
                        distancia_2 = distancia
                        distancia = nueva_distancia
                        indice_similar = j

                # Una vez que se termine de comparar cada frame de video con todos los comerciales, escribir una linea
                # en similares con los datos solicitados: nombre episodio tv, nombre comercial, distancia.
                respuesta = ""
                respuesta += iter_television[i]+"\t"
                respuesta += iter_comerciales[indice_similar]+"\t"
                respuesta += str(round(distancia, 1))+"\t"

                similares.write(respuesta+"\n")

# Imprimir en terminal el tiempo de ejecución
print("--- Tiempo de ejecución: %s segundos ---" % (time.time() - tiempo_inicial))