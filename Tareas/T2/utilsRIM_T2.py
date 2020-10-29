import numpy as np
import cv2


# distancia_manhattan: array(float) array(float) -> float
# devuelve la distancia de manhattan entre los vectores a y b
def distancia_manhattan(a, b):
    return np.abs(a - b).sum()

# proporcionFrames: int string -> flot
# Recibe la cantidad de frames encontrados, el nombre del directorio donde buscar descriptores_comerciales
# y entrega un numero entre 0 y 1 representando la magnitud n_frames_encontrados / n_frames_totales_del_comercial
def proporcionFrames(n_frames, comercial, path):
    frames_totales = 0
    with open(path+"descriptores_comerciales/info_descriptores", 'r') as info_comerciales:
        # Leer archivo como objeto iterable, separando por saltos de linea
        iter_comerciales = info_comerciales.read().split('\n')
        for linea in iter_comerciales:
            if comercial in linea:
                frames_totales+=1
        return n_frames/frames_totales

# canny_automatizado: image int double -> image
# Aplica el detector de bordes Canny a la imagen entregada, redimensionada a 'tamaño' x 'tamaño',
# Encontrando de forma automática los valores para high_treshold y low_treshold basandose en
# el promedio y un valor de desviación estándar (por defecto 1/3).
# Se utiliza L2 para encontrar la magnitud del gradiente.
def canny_automatizado(imagen, tamaño, sigma=0.33):
    media = np.median(imagen)
    img_redim = cv2.resize(imagen, (tamaño, tamaño))
    low_tresh = int(max(0, (1.0 - sigma) * media))
    high_tresh = int(min(255, (1.0 + sigma) * media))
    img_canny = cv2.Canny(img_redim, low_tresh, high_tresh, L2gradient=True)
    return img_canny

# diferencia_tolerable: float float float -> boolean
# Retorna True si a y b estan a una distancia menor o igual a epsilon, False si no.
def diferencia_tolerable(a, b, epsilon):
    return np.abs(a-b) <= epsilon




