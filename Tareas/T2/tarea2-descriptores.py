import sys
import os.path
import cv2
import time
import utilsRIM_T2 as utils
import numpy as np

# INICIAR CRONÓMETRO PARA EL TIEMPO DE EJECUCIÓN
tiempo_inicial = time.time()

# VERIFICAR RECEPCIÓN CORRECTA DE PARAMETROS
if len(sys.argv) < 3:
    print("Uso: {} [videos_dir] [descriptores_dir]".format(sys.argv[0]))
    sys.exit(1)

# IDENTIFICAR PARÁMETROS
videos_dir = sys.argv[1]
descriptores_dir = sys.argv[2]

# REVISAR EXISTENCIA DEL DIRECTORIO ENTREGADO
if not os.path.isdir(videos_dir):
    print("no existe directorio {}".format(videos_dir))
    sys.exit(1)

# DEFINICIÓN DE PARÁMETROS PRINCIPALES
segs = 0.3  # Tiempo entre cada frame a retener, en segundos
tamaño = 60  # El tamaño con el cual se hará resize a cada frame

# ABRIR DOCUMENTOS DESTINO
os.makedirs(descriptores_dir)
descriptores = []
info = open(descriptores_dir + "/info_descriptores", 'w')
numero_frames = open(descriptores_dir + "/numero_frames", 'w')

# ITERAR SOBRE CADA VIDEO DEL DIRECTORIO: PROCESAMIENTO
for videofile in os.listdir(videos_dir):
    video = cv2.VideoCapture(videos_dir + "/" + videofile)

    # Reconocer cuantos frames por segundo tiene cada video
    fps = video.get(cv2.CAP_PROP_FPS)

    # Para avanzar 'segs' segundos entre cada "muestreo" necesitamos avanzar 'fps*segs' frames
    multiplicador = round(fps * segs, 0)

    # Inicializamos la lectura como exitosa al inicio de cada video y el conteo de frames en 0
    lectura_exitosa = True
    nframes = 0

    # PROCESAMIENTO
    while lectura_exitosa:
        # Leemos un frame del video. Esto actualiza el valor de 'lectura_exitosa'.
        lectura_exitosa, frame = video.read()

        # Obtenemos el numero del frame actual
        frameID = video.get(1)

        # Si el frame corresponde a un multiplo de fps*segs, lo procesamos
        if frameID % multiplicador == 0:
            # Aplicamos Canny sobre el frame. Este sera el descriptor a usar.
            canny_frame = utils.canny_automatizado(frame, tamaño)

            # Guardamos la imagen filtrada en un arreglo para luego guardarlo en binario,
            # y los datos nombre video y frame en un archivo de texto.
            descriptores.append(canny_frame)
            info.write(videofile + "\t" + str(round(frameID / fps, 2)) + "\n")

            # Aumentar el recuento de frames de este video en 1
            nframes += 1

    # Si ya se leyo el video completo o hubo un error de lectura, liberar el video y guardar la cantidad
    # de frames leidos
    video.release()
    numero_frames.write(videofile + "\t" + str(nframes) + "\n")

# Una vez que se procesaron todos los videos, se guardan los descriptores en un archivo binario.
np_descriptores = np.array(descriptores)
np.save(descriptores_dir + "/" + "descriptores", np_descriptores)

# Imprimir en terminal el tiempo de ejecución
print("--- Tiempo de ejecución: %s segundos ---" % (time.time() - tiempo_inicial))
