import sys
import os.path
import utilsRIM_T3 as utils
import time

# ----------------VARIABLES DETERMINANTES EN LA EFICIENCIA Y EFICACIA DEL PROGRAMA-------------------------------------#
factor = 2              # Debe coincidir con factor en tarea3-descriptores.py
min_votos = 5           # Cantidad minima de votos de una secuencia para considerarse como comercial válido.
                        # Valor recomendado: 5
gap_max = 4             # Cantidad máxima de 'saltos' permitidos en una misma secuencia de un comercial antes de
                        # descartarlo como tal.
                        # Valor recomendado: 4
confianza_min = 0.3     # Umbral de confianza. Valor mínimo que debe cumplir una secuencia de 'comercial válido' para
                        # ser finalmente escrito en el archivo de detecciones preeliminar (dup_detecciones).
                        # Valor recomendado: 0.3
pasadas = 1             # Cantidad de pasadas que se le darán al archivo de detecciones preeliminar fusionando
                        # duplicados.
                        # Valor recomendado: 1
# ---------------------------------------------------------------------------------------------------------------------#

# INICIAR CRONÓMETRO PARA EL TIEMPO DE EJECUCIÓN
tiempo_inicial = time.time()

# RECIBIR Y VERIFICAR PARÁMETROS
if len(sys.argv) < 3:
    print("Uso: {} [similares_file] [detecciones_file]".format(sys.argv[0]))
    sys.exit(0)

similares_file = sys.argv[1]
detecciones_file = sys.argv[2]
nombre_descriptores = "descriptores_comerciales"

if not os.path.isfile(similares_file):
    print("no existe archivo {}".format(similares_file))
    sys.exit(0)

# ENCONTRAR PATH A WORK_X
path = similares_file.split("/")[:-1]
carpeta = ""
for p in path:
    carpeta += p

# CREAR ARCHIVO DE DUPLICADOS.
# Si la cantidad de pasadas es mayor a 0, crear archivo preeliminar.
if pasadas > 0:
    detecciones_dup = open(detecciones_file + "_dup", 'w')
else:
    detecciones = open(detecciones_file, 'w')

# ITERAR SOBRE LAS FILAS DE SIMILARES
with open(similares_file, "r", encoding="utf-8") as similares:
    iter_similares = similares.read().split('\n')

    # CREACION DEL DICCIONARIO
    # Utilizaremos un diccionario para guardar los votos, de la siguiente forma:
    # El diccionario mapeará 3-tuplas.
    # Las llaves serán los nombres de los comerciales
    # El primer valor en la tupla corresponderá a la cantidad de votos
    # El segundo valor en la tupla será un bool indicando si estuvo presente en la fila actual
    # El tercer valor será un contador del gap que dicho comercial lleva hasta el momento.
    dic = dict()

    # Intentar leer la primera fila para inicializar el diccionario.
    try:
        primera_fila = iter_similares[0].split('\t')
        nombre_tv_anterior, n_tv_anterior = utils.separar_nombre_numero(primera_fila[0])
    except:
        raise Exception("Archivo similares está vacío o no se logró abrir para lectura exitosamente.")

    # ITERAR SOBRE TODAS LAS FILAS DEL DOCUMENTO
    for i in range(1, len(iter_similares) - 1):
        valores_fila = iter_similares[i].split('\t')
        television_wav = valores_fila[0]
        nombre_tv, n_tv = utils.separar_nombre_numero(television_wav)

        # MARCAR TODOS LOS ELEMENTOS COMO INICIALMENTE NO PRESENTES EN ESTA FILA
        for comercial in list(dic.keys()):
            valor = dic.pop(comercial)
            nuevo_valor = (valor[0], False, valor[2])
            dic[comercial] = nuevo_valor

        # VERIFICAR CONDICIONES DE PRESENCIA, MARCAR TRUE.
        if nombre_tv == nombre_tv_anterior and n_tv == n_tv_anterior + 1:
            # iterar sobre elementos de la linea
            for j in range(1, len(valores_fila), 2):
                comercial_wav = valores_fila[j]
                nombre_comercial, n_comercial = utils.separar_nombre_numero(comercial_wav)
                n_comercial_ant = n_comercial - 1
                comercial_anterior_wav = nombre_comercial + ".wav" + str(n_comercial_ant)
                if comercial_anterior_wav not in dic.keys() and comercial_wav not in dic.keys():
                    # Si el comercial es nuevo, agregarlo al diccionario con los valores iniciales
                    dic[comercial_wav] = (1, True, 0)
                elif comercial_anterior_wav in dic.keys():
                    if (comercial_wav in dic.keys() and dic[comercial_wav][0] < min_votos) \
                            or comercial_wav not in dic.keys():
                        # Si el comercial está en el diccionario, cambiar su última aparición con esta nueva + 1 voto
                        # y reiniciar su contador de gap pues retomo la secuencia.
                        votos = dic.pop(comercial_anterior_wav)
                        dic[comercial_wav] = (votos[0] + 1, True, 0)
        nombre_tv_anterior, n_tv_anterior = nombre_tv, n_tv

        # TRATAR LOS COMERCIALES QUE NO SE PRESENTARON EN ESTA PASADA
        for comercial in list(dic):
            if dic[comercial][1] == False:
                valores = dic.pop(comercial)
                votos = valores[0]
                gap_actual = valores[2]
                # Si en esta pasada se alcanza el limite de gap, verificar si se cumple la condición sobre votos y
                # confianza, escribiendo en tal caso la linea correspondiente en detecciones. Caso contrario, descartar.
                if gap_actual + 1 == gap_max:
                    if votos - gap_max > min_votos:
                        nombre_comercial, n_comercial = utils.separar_nombre_numero(comercial)
                        confianza = utils.proporcionDescr(votos - gap_max, nombre_comercial,
                                                          carpeta + "/" + nombre_descriptores + "/n_descriptores")
                        if confianza >= confianza_min:
                            detecciones_dup.write(
                                nombre_tv + ".mp3" + "\t" + str(round((n_tv - votos - gap_max) / 2, 1)) + "\t" +
                                str(round((votos - gap_max) / 2.0, 1)) + "\t" + nombre_comercial + ".mp3" +
                                "\t" + str(round(confianza, 3)) + "\n")

                # Si aún no se alcanza el limite de gap, sumar un voto y mantener en el diccionario, más aumentando
                # también la variable gap_actual.
                elif gap_actual + 1 <= gap_max:
                    comercial_nombre, wav_numero = utils.separar_nombre_numero(comercial)
                    comercial_wav_sgte = comercial_nombre + ".wav" + str(wav_numero + 1)
                    dic[comercial_wav_sgte] = (votos + 1, False, gap_actual + 1)

# FUSIÓN DE POSIBLES DUPLICADOS
# Al trabajar con valores bajos de confianza_min (<0.4) es posible que se generen duplicados consecutivos en el archivo
# detecciones. Las instrucciones a continuación permiten corregir este aspecto.
# Importante: para su funcionamiento se requiere que el valor de pasadas sea mayor o igual a 1.
i = 0
min_cfza_pasadas = 0.45  # Valor minimo de confianza que se le pedirá a una fila del archivo detecciones_dup
# para ser considerada como una detección independiente y no fusionarla aún cuando las
# lineas previas o siguientes correspondan al mismo comercial.

while i < pasadas:
    # ITERAR SOBRE LAS FILAS DEL ARCHIVO DETECCIONES_DUP.TXT ESCRIBIENDO EN DETECCIONES.TXT
    with open(detecciones_file + "_dup", 'r') as detecciones_dup:
        with open(detecciones_file, 'w') as detecciones_final:
            # Leer archivo como objeto iterable, separando por saltos de linea
            iter_detecciones_dup = detecciones_dup.read().split('\n')
            i = 0
            while i < len(iter_detecciones_dup) - 2:
                valores_act = iter_detecciones_dup[i].split('\t')
                valores_sig = iter_detecciones_dup[i + 1].split('\t')

                # Si la deteccion actual y la siguiente corresponden al mismo comercial, y al menos una de ellas tiene
                # un bajo nivel de confianza, se unen en la misma detección sumando sus valores.
                if valores_act[0] == valores_sig[0] and valores_act[3] == valores_sig[3] and (
                        float(valores_act[4]) <= min_cfza_pasadas or float(valores_sig[4]) <= min_cfza_pasadas):
                    suma_tiempos = str(float(valores_act[2]) + float(valores_sig[2]))
                    suma_confianzas = str(float(valores_act[4]) + float(valores_sig[4]))
                    detecciones_final.write(valores_act[0] + '\t' + valores_act[1] + '\t' + suma_tiempos + \
                                            '\t' + valores_act[3] + '\t' + suma_confianzas + '\n')
                    i += 1
                # Si la deteccion actual tiene suficiente confianza por si sola o no se puede reunir con la siguiente,
                # la mantenemos.
                else:
                    detecciones_final.write(iter_detecciones_dup[i] + '\n')
                i += 1

            # Caso borde: la última linea no se unió a la penúltima (y ya que no es evaluada en el while, la evaluamos aparte).
            if i < len(iter_detecciones_dup) - 1:
                ultima_linea = iter_detecciones_dup[i].split('\t')
                if float(ultima_linea[4]) > min_cfza_pasadas:
                    detecciones_final.write(iter_detecciones_dup[i])
    i += 1

# IMPRIMIR TIEMPO TOTAL DE EJECUCIÓN
print("--- Tiempo total detección: %s segundos ---" % (time.time() - tiempo_inicial))
