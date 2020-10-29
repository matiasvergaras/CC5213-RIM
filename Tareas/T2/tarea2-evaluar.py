import sys
import os.path
import subprocess


class Deteccion:
    def __init__(self, id_deteccion, television, desde, largo, comercial, score):
        self.id_deteccion = id_deteccion
        self.television = television
        self.desde = desde
        self.largo = largo
        self.comercial = comercial
        self.score = score

    def interseccion(self, otra):
        if self.television != otra.television or self.comercial != otra.comercial:
            return 0
        ini1 = self.desde
        end1 = self.desde + self.largo
        ini2 = otra.desde
        end2 = otra.desde + otra.largo
        inter = min(end1, end2) - max(ini1, ini2)
        union = max(end1, end2) - min(ini1, ini2)
        if inter <= 0 or union <= 0:
            return 0
        return inter / union


def get_filename(filepath):
    name = filepath.lower().strip()
    if name.rfind('/') >= 0:
        name = name[name.rfind('/') + 1:]
    if name.rfind('\\') >= 0:
        name = name[name.rfind('\\') + 1:]
    return name


def leer_archivo_detecciones(filename, with_scores):
    if not os.path.isfile(filename):
        raise Exception("no existe el archivo {}".format(filename))
    detecciones = []
    cont_lineas = 0
    with open(filename) as f:
        for linea in f:
            cont_lineas += 1
            try:
                linea = linea.rstrip("\r\n")
                # se ignoran lineas vacias o comentarios
                if linea == "" or linea.startswith("#"):
                    continue
                partes = linea.split("\t")
                if with_scores and len(partes) != 5:
                    raise Exception("incorrecto numero de columnas (se esperan 5 columnas separadas por un tabulador")
                if not with_scores and len(partes) != 4:
                    raise Exception("incorrecto numero de columnas (se esperan 4 columnas separadas por un tabulador")
                # nombre de video (sin ruta)
                television = get_filename(partes[0])
                if television == "":
                    raise Exception("nombre television invalido")
                # nombre de comercial (sin ruta)
                comercial = get_filename(partes[3])
                if comercial == "":
                    raise Exception("nombre comercial invalido")
                # los tiempos pueden incluir milisegundos
                desde = round(float(partes[1]), 3)
                if desde < 0:
                    raise Exception("valor incorrecto desde={}".format(desde))
                largo = round(float(partes[2]), 3)
                if largo <= 0:
                    raise Exception("valor incorrecto largo={}".format(largo))
                # el score
                score = 0
                if with_scores:
                    score = float(partes[4])
                    if score <= 0:
                        raise Exception("valor incorrecto score={}".format(score))
                det = Deteccion(cont_lineas, television, desde, largo, comercial, score)
                detecciones.append(det)
            except Exception as ex:
                print("Error {} (linea {}): {}".format(filename, cont_lineas, ex))
    print("{} detecciones en archivo {}".format(len(detecciones), filename))
    return detecciones


class ResultadoDeteccion:
    def __init__(self, deteccion):
        self.deteccion = deteccion
        self.es_incorrecta = False
        self.es_repetida = False
        self.es_correcta = False
        self.gt = None
        self.iou = 0


class Metricas:
    def __init__(self, threshold):
        self.threshold = threshold
        self.total_gt = 0
        self.total_detecciones = 0
        self.correctas = 0
        self.incorrectas = 0
        self.recall = 0
        self.precision = 0
        self.f1 = 0
        self.iou = 0


class Evaluacion:
    def __init__(self, file_detecciones, file_gt):
        # cargar las detecciones
        self.detecciones = leer_archivo_detecciones(file_detecciones, True)
        # cargar el ground-truth
        groundtruth = leer_archivo_detecciones(file_gt, False)
        # seleccionar del ground-truth solo los videos de television de las detecciones
        videos_tv = set()
        for det in self.detecciones:
            videos_tv.add(det.television)
        # filtrar gt relevante
        self.detecciones_gt = []
        for gt in groundtruth:
            if gt.television in videos_tv:
                self.detecciones_gt.append(gt)
        # donde se guarda el resultado de la evaluacion
        self.resultado_por_deteccion = list()
        self.resultado_global = None

    def evaluar_cada_deteccion(self):
        # ordenar detecciones por score de mayor a menor
        self.detecciones.sort(key=lambda x: x.score, reverse=True)
        # para descartar las detecciones duplicadas
        ids_encontradas = set()
        # revisar cada deteccion
        for det in self.detecciones:
            # evaluar cada deteccion si es correcta a no
            gt_encontrada, iou = self.buscar_deteccion_en_gt(det)
            # retorna resultado
            res = ResultadoDeteccion(det)
            if gt_encontrada is None:
                res.es_incorrecta = True
            elif gt_encontrada.id_deteccion in ids_encontradas:
                res.es_repetida = True
            else:
                res.es_correcta = True
                res.gt = gt_encontrada
                res.iou = iou
                ids_encontradas.add(gt_encontrada.id_deteccion)
            self.resultado_por_deteccion.append(res)
        # ordenar los resultados como el archivo de entrada
        self.resultado_por_deteccion.sort(key=lambda x: x.deteccion.id_deteccion)

    def buscar_deteccion_en_gt(self, deteccion):
        gt_encontrada = None
        iou = 0
        # busca en gt la deteccion que tiene mayor interseccion
        for det_gt in self.detecciones_gt:
            interseccion = deteccion.interseccion(det_gt)
            if interseccion > iou:
                gt_encontrada = det_gt
                iou = interseccion
        return gt_encontrada, iou

    def calcular_metricas(self):
        # todos los umbrales posibles
        all_scores = set()
        for res in self.resultado_por_deteccion:
            if res.es_correcta:
                all_scores.add(res.deteccion.score)
        all_scores.add(0)
        # calcular las metricas para cada score y seleccionar el mejor
        for score in sorted(list(all_scores), reverse=True):
            met = self.evaluar_con_threshold(score)
            if self.resultado_global is None or met.f1 > self.resultado_global.f1:
                self.resultado_global = met

    def evaluar_con_threshold(self, score_threshold):
        met = Metricas(score_threshold)
        met.total_gt = len(self.detecciones_gt)
        suma_iou = 0
        for res in self.resultado_por_deteccion:
            # ignorar detecciones con score bajo el umbral
            if res.deteccion.score < score_threshold:
                continue
            met.total_detecciones += 1
            if res.es_correcta:
                met.correctas += 1
                suma_iou += res.iou
            if res.es_incorrecta or res.es_repetida:
                met.incorrectas += 1
        if met.correctas > 0:
            met.recall = met.correctas / met.total_gt
            met.precision = met.correctas / met.total_detecciones
        if met.precision > 0 and met.recall > 0:
            met.f1 = (2 * met.precision * met.recall) / (met.precision + met.recall)
        if met.correctas > 0:
            met.iou = suma_iou / met.correctas
        return met

    def imprimir_resultado_por_deteccion(self):
        if len(self.resultado_por_deteccion) == 0:
            return
        print("Resultado de las {} detecciones:".format(len(self.resultado_por_deteccion)))
        for res in self.resultado_por_deteccion:
            s1 = ""
            s2 = ""
            if res.es_correcta:
                s1 = " OK)"
                s2 = " //IoU={:.1%} gt=({} {})".format(res.iou, res.gt.desde, res.gt.largo)
            elif res.es_repetida:
                s1 = "dup)"
            elif res.es_incorrecta:
                s1 = " --)"
            d = res.deteccion
            print(" {} {} {} {} {} {} {}".format(s1, d.television, d.desde, d.largo, d.comercial, d.score, s2))

    def imprimir_resultado_global(self):
        if self.resultado_global is None:
            return
        m = self.resultado_global
        print(" {} detecciones en el GT".format(m.total_gt))
        print(" {} detecciones en el archivo a evaluar".format(len(self.resultado_por_deteccion)))
        print(" Al usar un score umbral={} se seleccionan {} detecciones con:".format(m.threshold, m.total_detecciones))
        print("    {} detecciones correctas, {} detecciones incorrectas".format(m.correctas, m.incorrectas))
        print("    Precision={:.3f} ({}/{})  Recall={:.3f} ({}/{})".format(m.precision, m.correctas,
                                                                           m.total_detecciones, m.recall, m.correctas,
                                                                           m.total_gt))
        print("    F1={:.3f}  IoU promedio={:.1%}".format(m.f1, m.iou))
        print()
        nota = 1 + 6 * ponderar(m.f1, 0.8, m.iou, 0.1)
        print("==> Nota resultados = {:.1f}   (pondera 60% en nota final de la tarea)".format(nota))
        if nota == 7:
            bonus = ponderar(m.f1 - 0.8, 0.2, m.iou - 0.1, 0.8)
            print("==> Bonus = {:.1f} puntos para otra tarea o mini-control".format(bonus))

        if m.total_gt == 0 and len(self.resultado_por_deteccion) > 0:
            print()
            print("¿archivo GT incorrecto?")
            return


def ponderar(valor_f1, max_f1, valor_iou, max_iou):
    nota_f1 = max(0, min(1, valor_f1 / max_f1))
    nota_iou = max(0, min(1, valor_iou / max_iou))
    return nota_f1 * 0.8 + nota_iou * 0.2


def evaluar_resultados(filename_detecciones, filename_gt):
    print()
    print("Evaluando detecciones en {} con {}".format(filename_detecciones, filename_gt));
    ev = Evaluacion(filename_detecciones, filename_gt)
    ev.evaluar_cada_deteccion()
    ev.calcular_metricas()
    ev.imprimir_resultado_por_deteccion()
    ev.imprimir_resultado_global()


def ejecutar_comandos(videos_comerciales, videos_television, work_dir):
    descriptores_television = "{}/descriptores_television".format(work_dir)
    descriptores_comerciales = "{}/descriptores_comerciales".format(work_dir)
    file_similares = "{}/similares.txt".format(work_dir)
    file_detecciones = "{}/detecciones.txt".format(work_dir)
    comandos = []
    # tareas en python
    comandos.append(["python", "tarea2-descriptores.py", videos_television, descriptores_television])
    comandos.append(["python", "tarea2-descriptores.py", videos_comerciales, descriptores_comerciales])
    comandos.append(["python", "tarea2-busqueda.py", descriptores_television, descriptores_comerciales, file_similares])
    comandos.append(["python", "tarea2-deteccion.py", file_similares, file_detecciones])
    # tareas en c++
    # comandos.append(["./tarea2-descriptores.py", videos_television, descriptores_television])
    # comandos.append(["./tarea2-descriptores.py", videos_comerciales, descriptores_comerciales])
    # comandos.append(["./tarea2-busqueda.py", descriptores_television, descriptores_comerciales, file_similares])
    # comandos.append(["./tarea2-deteccion.py", filename_similares, file_detecciones])
    # tareas en java
    # comandos.append(["java", "tarea2-descriptores.py", videos_television, descriptores_television])
    # comandos.append(["java", "tarea2-descriptores.py", videos_comerciales, descriptores_comerciales])
    # comandos.append(["java", "tarea2-busqueda.py", descriptores_television, descriptores_comerciales, file_similares])
    # comandos.append(["java", "tarea2-deteccion.py", file_similares, file_detecciones])

    for comando in comandos:
        print()
        print("INICIANDO: {}".format(" ".join(comando)))
        code = subprocess.call(comando)
        if code != 0:
            print("ERROR!")
            sys.exit()

    return file_detecciones


# inicio
if len(sys.argv) < 3:
    print("CC5213 - Evaluación Tarea 2  (2020-2)")
    print("Uso: {} [dataset_dir] [work_dir]".format(sys.argv[0]))
    sys.exit(1)

dataset_dir = sys.argv[1]
work_dir = sys.argv[2]

comerciales = "{}/comerciales".format(dataset_dir)
television = "{}/television".format(dataset_dir)
filename_gt = "{}/gt.txt".format(dataset_dir)

if not os.path.isdir(comerciales) or not os.path.isdir(television) or not os.path.isfile(filename_gt):
    print("ruta {} no es válida".format(dataset_dir))
    sys.exit(1)

filename_detecciones = ejecutar_comandos(comerciales, television, work_dir)

evaluar_resultados(filename_detecciones, filename_gt)
