#Autor: Matias Vergara Silva
#Basado en el Material del curso Recuperacion de Informacion Multimedia de la Universidad de Chile,
#Creado por el profesor Juan Barrios https://www.juan.cl

import time
start_time = time.time()

import sys
import utilsRIM as RIM

#programa_principal_buscar: None -> None
#Revisa que los argumentos entregados por sys sean los correspondientes y llama
#a la(s) funcion(es) de descripion implementada(s).
def programa_principal_procesar():
    # Revisamos que la cantidad de argumentos ingresados sea la correcta
    if len(sys.argv) != 3:
        print("Nombre de argumentos:", len(sys.argv) - 1, 'argumentos. ')
        print("Debe llamar a la funcion con 2 argumentos: dir_imagenes_R y datos_R")
        sys.exit(1)
    else:
        dir_imgR = sys.argv[1]
        dir_datos = sys.argv[2]
        #Llamadas a los metodos de descripcion implementados
        RIM.vector_intensidad(dir_imgR, 30, dir_datos)


#Ejecución con reloj
programa_principal_procesar()
print("--- Tiempo de procesamiento: %s segundos ---" % (time.time() - start_time))
