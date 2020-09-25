# encoding: utf-8
#Autor: Juan Barrios https://www.juan.cl
#Modificaciones por Matias Vergara
#Basado en el Material del curso Recuperacion de Informacion Multimedia de la Universidad de Chile

import sys 
import os
import numpy as np
import cv2


#abrir_imagen: string -> img as array
#abre la imagen del path indicado y la entrega como arreglo.
def abrir_imagen(filename):
    imagen_color = cv2.imread(filename, cv2.IMREAD_COLOR)
    if imagen_color is None:
        raise Exception("error abriendo {}".format(filename))
    return imagen_color


#vector_intensidad: string int string -> np.array, np.array
#recibe el nombre de la carpeta de imagenes (debe estar en el path actual, el tamaño a trabajar (en pixeles por lado),
# y un parametro opcional de directorio donde guardar los arreglos creados. Calcula el Vector (flatten) de Intensidades
# de la imagen y lo guarda/retorna junto a un archivo de nombres
#de img's.
def vector_intensidad(dir_img, tamaño, dir_to_save=""):
    #Calculamos la cantidad de pixeles a almacenar por imagen
    pixeles = tamaño * tamaño
    #Contamos la cantidad de imagenes JPG en la carpeta
    nimagen = 0
    for filename in os.listdir(dir_img):
        if filename.endswith(".jpg"):
            nimagen += 1
    #Arreglo 2D para guardar la info una vez procesada y 1D para nombres
    imgProcesadas = np.zeros((nimagen, pixeles), dtype = int)
    nombres = np.array([])
    #Contador para indicar la cantidad de archivos ignorados
    contadorBadFormat = 0
    #Contador para ver en que posicion de imgProcesadas vamos
    indice = 0
    #Iteracion sobre cada archivo en la carpeta de imagenes
    for filename in os.listdir(dir_img):
        #Verificamos extension jpg
        if filename.endswith(".jpg"):
            #Redimensionamos y convertimos a escala de grises
            pathinput = sys.path[0] + '/' + dir_img + '/' + filename
            imagen_color = abrir_imagen(pathinput)
            imagen_resize = cv2.resize(imagen_color, (tamaño, tamaño))
            imagen_gris = cv2.cvtColor(imagen_resize, cv2.COLOR_BGR2GRAY)
            #Convertimos la imagen a un solo vector (1D) y guardamos en matriz imgProcesadas
            flatten = np.asarray(imagen_gris).reshape(-1)
            imgProcesadas[indice] = flatten
            #Rescatamos el nombre de la imagen mediante una actualizacion del array nombres.
            nombres = np.append(nombres, filename)
            indice += 1
        else:
            #Si no se verifica la condición de extensión, agregar 1 al contador de archivos no leídos.
            contadorBadFormat += 1
    print("Se han encontrado", contadorBadFormat, "archivos en formato no JPG en " + dir_img +".")
    #Guardamos la matriz imgProcesadas y el arreglo de nombres en archivos.
    if dir_to_save!="":
        np.savetxt(dir_to_save + "/" + "dataImgToVector.txt", imgProcesadas, fmt='%i')
        np.savetxt(dir_to_save + "/" + "namesImg.txt", nombres, fmt='%s')
    #Retornamos la matriz y el vector de nombre en caso de que sean necesarios.
    return imgProcesadas, nombres

