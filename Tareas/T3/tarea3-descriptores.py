import sys
import os
import utilsRIM_T3 as utils
import numpy as np
import time
# ----------------VARIABLES DETERMINANTES EN LA EFICIENCIA Y EFICACIA DEL PROGRAMA-------------------------------------#
factor = 2 # Si modifica factor en este script debe realizarlo también en tarea3-deteccion.py
# ---------------------------------------------------------------------------------------------------------------------#

# INICIAR CRONÓMETRO PARA EL TIEMPO DE EJECUCIÓN
tiempo_inicial = time.time()

# RECIBIR CANTIDAD INDICADA DE PARÁMETROS
if len(sys.argv) < 3:
    print("Uso: {} [audios_dir] [descriptores_dir]".format(sys.argv[0]))
    sys.exit(0)

audios_dir = sys.argv[1]
descriptores_dir = sys.argv[2]

if not os.path.isdir(audios_dir):
    print("no existe directorio {}".format(audios_dir))
    sys.exit(0)

# CREAR DIRECTORIOS DE DESTINO
os.makedirs(descriptores_dir + "/wav_files")
# os.makedirs(descriptores_dir + "/descriptores_bin")
info = open(descriptores_dir + "/info_descriptores", 'w')
n_descr = open(descriptores_dir + "/n_descriptores", 'w')

# CONVERTIR MP3 A WAV
print("-------- INICIANDO: Conversion a wav ---------")
for audiofile in os.listdir(audios_dir):
    print("Convirtiendo " + audiofile + " a wav")
    file_wav = utils.convertir_a_wav(audios_dir + "/" + audiofile,
                                     descriptores_dir + "/wav_files/" + audiofile[:-3] + "wav")


# CALCULAR MFCC PARA CADA AUDIO, GUARDAR NOMBRE EN TXT Y GUARDAR DESCRIPTOR EN BINARIO
wavfiles = os.listdir(descriptores_dir + "/wav_files/")
wavfiles = utils.sorted_alphanumeric(wavfiles)
with open(descriptores_dir + "/descriptores.npy", 'ab') as doc_descr:
    for wavfile in wavfiles:
        descriptores = utils.create_audio_descriptors(descriptores_dir + "/wav_files/" + wavfile, 2)
        i = 0
        for descriptor in descriptores:
            info.write(wavfile + str(i) + "\n")
            np.save(doc_descr , descriptor)
            i+=1
        n_descr.write(wavfile + '\t' + str(i) + "\n")


# IMPRIMIR TIEMPO TOTAL DE EJECUCIÓN
print("--- Tiempo total descriptores: %s segundos ---" % (time.time() - tiempo_inicial))
