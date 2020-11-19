import librosa
from pydub import AudioSegment
import re
import numpy as np

# Autor: Juan Manuel Barrios
# Fuente: CC5213 - Anexo 7.1. - Código python
def convertir_a_wav(file_mp3, file_wav):
    sound = AudioSegment.from_mp3(file_mp3)
    sound.export(file_wav, format="wav")

# Autor: Juan Manuel Barrios
# Fuente: CC5213 - Anexo 7.1. - Código python
def create_audio_descriptors(file_wav, factor):
    y, sr = librosa.load(file_wav)
    segundos = len(y) / sr
    # revisar parámetros de MFCC
    mfcc = librosa.feature.mfcc(y, n_mfcc=80, n_fft = int(sr/factor), hop_length = int(sr/factor))
   # print("audio {:.1f} segundos, {} descriptores de {}-d".format(segundos, mfcc.shape[1], mfcc.shape[0]))
    return mfcc.transpose()

# Autor: user136036
# Fuente: https://stackoverflow.com/questions/4813061/non-alphanumeric-list-order-from-os-listdir
# Para ordenar alfanuméricamente un listdir
def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)

# proporcionDescr: int string -> flot
# Recibe la cantidad de descriptores encontrados, el nombre del directorio donde buscar n_descr
# y entrega un numero entre 0 y 1 representando la magnitud n_descr_encontrados / n_descr_totales
def proporcionDescr(n_descr, comercial, path):
    descr_totales = 0
    with open(path, 'r') as info_comerciales:
        # Leer archivo como objeto iterable, separando por saltos de linea
        iter_comerciales = info_comerciales.read().split('\n')
        for linea in iter_comerciales:
            if comercial in linea:
                arr_linea = linea.split('\t')
                descr_totales = int(arr_linea[1])
                break
        return round(n_descr/descr_totales, 3)


# distancia_manhattan: array(float) array(float) -> float
# devuelve la distancia de manhattan entre los vectores a y b
def distancia_manhattan(a, b):
    return np.abs(a - b).sum()

# Para separar un string del tipo "nombre.wavNUMERO" en nombre, NUMERO.
# el numero es retornado como int.
def separar_nombre_numero(string):
    aux = string.split('.')
    return aux[0], int(aux[1][3:])


# Para separar un audio en wav en distintos segmentos de largo split_length
# El audio debe hallarse en in_path con nombre file_name. Los segmentos se guardan en out_path.
# Recomendado usarlo si se desea procesar videos demasiado largos para evitar problemas de memoria.
def split_wav(in_path, file_name, split_length, out_path):
    y, sr = librosa.load(in_path + file_name)
    segundos = len(y) / sr
    t1 = 0
    t2 = split_length
    cont = 0
    nuevoAudio = AudioSegment.from_wav(in_path + file_name)
    while t2 < segundos * 1000:
        split = nuevoAudio[t1:t2]
        split.export(out_path + file_name[0:-3] + "split" + str(cont), format="wav")
        t1 += split_length
        t2 += split_length
        cont += 1
