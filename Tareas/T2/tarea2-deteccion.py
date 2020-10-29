import sys
import os.path
import utilsRIM_T2 as utils
import time

#INICIAR CRONÓMETRO PARA EL TIEMPO DE EJECUCIÓN
tiempo_inicial = time.time()

# RECIBIR PARAMETROS ADECUADOS
if len(sys.argv) < 3:
    print("Uso: {} [similares_file] [detecciones_file]".format(sys.argv[0]))
    sys.exit(1)

# IDENTIFICAR PARÁMETROS
similares_file = sys.argv[1]
detecciones_file = sys.argv[2]

# RESCATAR PATH EN EL QUE SE ENCUENTRAN LOS ARCHIVOS. Sera necesario para el calculo de confianza.
filepath = similares_file.split("/")
filepath.pop()
real_path = ""
for directorio in filepath:
    real_path+=directorio+'/'

# REVISAR EXISTENCIA DE ARCHIVO SIMILARES
if not os.path.isfile(similares_file):
    print("no existe archivo {}".format(similares_file))
    sys.exit(1)

# PARAMETRO DETERMINANTE: LARGO MINIMO DE COMERCIALES EN SEGUNDOS
min_segs = 3

# BUSCAR SIMILARES
with open(detecciones_file, 'w') as detecciones:
    with open(similares_file, 'r') as similares:

        # Leer archivo como objeto iterable, separando por saltos de linea
        iter_similares = similares.read().split('\n')

        # Leer cada entrada del archivo (linea) como un arreglo de strings, separados por tabulaciones
        valores_inicio = iter_similares[0].split('\t')

        # Descubrir el paso temporal con el que se procesaron los descriptores mediante la diferencia de tiempo
        # entre la segunda linea y la primera
        delta_t_descriptores = float(iter_similares[1].split('\t')[1]) - float(valores_inicio[1])

        # Inicializar los parametros a evaluar para un posible candidato a comercial
        tiempo_inicio_tv = valores_inicio[1]
        comercial_inicio = valores_inicio[2]
        tiempo_inicio_comerc = valores_inicio[3]
        tiempo_ultimo_frame = tiempo_inicio_comerc
        # Conteo de frames que han sido aproximados a un mismo comercial
        nframes = 1

        #Para iterar sobre los pares de similares, desde el segundo
        i = 1

        while i < len(iter_similares) - 2:

            # Tratamiento de similares como arreglo
            valores_act = iter_similares[i].split('\t')
            comercial_act = valores_act[2]
            tiempo_act = valores_act[3]


            # Si el candidato a comercial se mantiene en este frame,
            # y dicho frame es posterior al ultimo aprobado, continuar.
            if comercial_act == comercial_inicio and tiempo_act>=tiempo_ultimo_frame:
                tiempo_ultimo_frame = tiempo_act
                nframes+=1
                i+=1

            # En caso contrario:
            else:
                #Si el candidato a comercial cambia en este frame, evaluar sus parámetros
                if comercial_act != comercial_inicio:
                    frame_final = iter_similares[i-1].split('\t')
                    tiempo_final_tv = frame_final[1]
                    tiempo_final_comerc = frame_final[3]

                    # Diferencia de tiempo entre tiempo tv y tiempo comercial debe ser casi exactamente igual.
                    delta_tv = float(tiempo_final_tv) - float(tiempo_inicio_tv)
                    delta_comerc = float(tiempo_final_comerc) - float(tiempo_inicio_comerc)

                    # Si es que dicha condición se cumple y el candidato esta presente por al menos 'min_segs' segundos
                    if utils.diferencia_tolerable(delta_tv, delta_comerc, 0.5) and nframes >= min_segs*(1/delta_t_descriptores):
                        # CALCULAR CONFIANZA COMO N FRAMES ENCONTRADOS/ N FRAMES TOTALES COMERCIAL
                        confianza = utils.proporcionFrames(nframes, comercial_inicio, real_path)
                        # ESCRIBIR DETECCIONES
                        detecciones.write(
                            valores_act[0] + "\t" + tiempo_inicio_tv + "\t" + str(delta_comerc) + "\t" +
                            frame_final[2] + "\t" + str(confianza) + "\n")

                # Si la condición sobre los tiempos no se cumplió, o ya se escribió una identificación,
                # Continuar buscando detecciones en los pares frame tv - frame comercial siguientes,
                # actualizando el candidato a comercial a mantener en los sig. frames.
                valores_inicio = iter_similares[i].split('\t')
                tiempo_inicio_tv = valores_inicio[1]
                comercial_inicio = valores_inicio[2]
                tiempo_inicio_comerc = valores_inicio[3]
                tiempo_ultimo_frame = tiempo_inicio_comerc
                nframes = 1
                i+=1

# Imprimir en terminal el tiempo de ejecución
print("--- Tiempo de ejecución: %s segundos ---" % (time.time() - tiempo_inicial))



