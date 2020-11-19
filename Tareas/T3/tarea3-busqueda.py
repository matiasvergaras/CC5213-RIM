import sys
import os.path
import time
import numpy as np
from pathlib import Path
import utilsRIM_T3 as utils

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

# CREAR PATHS A USAR
p_descr_television = Path(descriptores_television_dir + "/descriptores.npy")
p_descr_comerciales = Path(descriptores_comerciales_dir + "/descriptores.npy")
p_info_television = Path(descriptores_television_dir + "/info_descriptores")
p_info_comerciales = Path(descriptores_comerciales_dir + "/info_descriptores")
p_similares = Path(similares_file)

with p_similares.open('w') as sf:
    with p_info_television.open('r') as inftv:
        iter_television = inftv.read().split('\n')
        with p_info_comerciales.open('r')as infcom:
            iter_comerciales = infcom.read().split('\n')
            with p_descr_television.open('rb') as dtv:
                fsztv = os.fstat(dtv.fileno()).st_size
                i = 0
                while dtv.tell() < fsztv:
                    #CARGAR UNA LINEA DE DESCRIPTOR DE TV A LA VEZ
                    descr_tv = np.load(dtv)
                    with p_descr_comerciales.open('rb') as dtc:
                        fszcom = os.fstat(dtc.fileno()).st_size
                        j = 0
                        # INICIAR INDICES DE DESCRIPTOR MAS CERCANO EN 0
                        i_similar1 = 0
                        i_similar2 = 0
                        i_similar3 = 0
                        i_similar4 = 0
                        # INICIAR DISTANCIAS EN APROX. MAXINT
                        dist_1 = 2**32
                        dist_2 = 2*+32
                        dist_3 = 2**32
                        dist_4 = 2**32

                        while dtc.tell() < fszcom:
                            # CARGAR UN DESCRIPTOR DE COMERCIAL A LA VEZ
                            descr_com = np.load(dtc)
                            # CALCULAR DISTANCIA Y ACTUALIZAR EL CONJUNTO DE DISTANCIAS, CUANDO SE HALLE UN MINIMO
                            nueva_dist = utils.distancia_manhattan(descr_tv, descr_com)
                            if nueva_dist < dist_1:
                                dist_4 = dist_3
                                dist_3 = dist_2
                                dist_2 = dist_1
                                dist_1 = nueva_dist
                                i_similar4 = i_similar3
                                i_similar3 = i_similar2
                                i_similar2 = i_similar1
                                i_similar1 = j
                            j+= 1

                    # ESCRIBIR EL COMERCIAL Y SUS 4 VECINOS MÁS CERCANOS EN EL ARCHIVO SIMILARES
                    respuesta = iter_television[i] + "\t"
                    respuesta += iter_comerciales[i_similar1] + "\t"
                    respuesta += str(round(dist_1, 1)) + "\t"
                    respuesta += iter_comerciales[i_similar2] + "\t"
                    respuesta += str(round(dist_2, 1)) + "\t"
                    respuesta += iter_comerciales[i_similar3] + "\t"
                    respuesta += str(round(dist_3, 1)) + "\t"
                    respuesta += iter_comerciales[i_similar4] + "\t"
                    respuesta += str(round(dist_4, 1))+ "\n"
                    sf.write(respuesta)
                    i+=1


# IMPRIMIR EN TERMINA EL TIEMPO DE EJECUCIÓN
print("--- Tiempo total busqueda: %s segundos ---" % (time.time() - tiempo_inicial))