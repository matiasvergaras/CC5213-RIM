import sys
import os.path
import subprocess


class GT:
    def __init__(self, tipo, imagen_q, imagen_r):
        self.tipo = tipo
        self.imagen_q = imagen_q
        self.imagen_r = imagen_r


class GroudTruth:
    def __init__(self):
        self.lista = list()
        self.gt_por_query = dict()
        self.total_por_tipo = dict()

    def leer_archivo_gt(self, filename):
        if not os.path.isfile(filename):
            raise Exception("no existe {}".format(filename))
        with open(filename) as f:
            for linea in f:
                linea = linea.rstrip("\r\n")
                if linea == "" or linea.startswith("#"):
                    continue
                partes = linea.split()
                if len(partes) != 3:
                    raise Exception("{}: archivo GT invalido".format(filename))
                if partes[0] not in ["Q", "C", "T", "V"]:
                    raise Exception("{}: archivo GT invalido".format(filename))
                gt = GT(partes[0], partes[1], partes[2])
                if gt.imagen_r == "-":
                    continue
                self.lista.append(gt)
                self.gt_por_query[gt.imagen_q] = gt
                self.total_por_tipo[gt.tipo] = self.total_por_tipo.get(gt.tipo, 0) + 1
        if len(self.lista) != 1600:
            raise Exception("{}: archivo GT invalido ({} queries)".format(filename, len(self.lista)))
        print("{} cargado ok".format(filename))

    def buscar_gt(self, imagen_q):
        if imagen_q not in self.gt_por_query:
            return None
        return self.gt_por_query[imagen_q]

    def total_queries(self):
        return len(self.gt_por_query)


nombres_tipos = dict()
nombres_tipos["Q"] = "CALIDAD"
nombres_tipos["C"] = "CROP"
nombres_tipos["T"] = "TEXTO+COLOR"
nombres_tipos["V"] = "VARIOS"


class Deteccion:
    def __init__(self, linea, imagen_q, imagen_r, distancia):
        self.linea = linea
        self.imagen_q = imagen_q
        self.imagen_r = imagen_r
        self.distancia = distancia


class Detecciones:
    def __init__(self):
        self.lista = list()

    def leer_archivo_detecciones(self, filename):
        if not os.path.isfile(filename):
            raise Exception("no existe {}".format(filename))
        cont_lineas = 0
        with open(filename) as f:
            for linea in f:
                cont_lineas += 1
                try:
                    linea = linea.rstrip("\r\n")
                    if linea == "" or linea.startswith("#"):
                        continue
                    partes = linea.split()
                    if len(partes) != 3:
                        raise Exception("formato incorrecto (se esperan 3 columnas)")
                    det = Deteccion(linea, partes[0], partes[1], float(partes[2]))
                    if det.distancia < 0:
                        raise Exception("formato incorrecto (distancia={})".format(det.distancia))
                    self.lista.append(det)
                except Exception as ex:
                    print("{} (linea {}): {}".format(filename, cont_lineas, ex))
                    sys.exit(1)
        print("{} detecciones en {}".format(len(self.lista), filename))


class Metricas:
    def __init__(self):
        self.correctas = 0
        self.incorrectas = 0
        self.ignoradas = 0
        self.duplicadas = 0
        self.precision = 0
        self.recall = 0
        self.f1 = 0
        self.correcta_por_tipo = dict()
        self.recall_por_tipo = dict()
        self.threshold = None

    def resultado_por_tipo(self):
        val = "  Resultados por tipo de query"
        for tipo in self.recall_por_tipo:
            val += "\n    {}-{:12s}={:4} ({:.0f}%)".format(tipo, nombres_tipos[tipo],
                                                           self.correcta_por_tipo[tipo],
                                                           100 * self.recall_por_tipo[tipo])
        return val

    def resultado_metricas1(self):
        val = "distancia_umbral={:7.4f}".format(self.threshold)
        val += "  respuestas={}".format(self.ignoradas + self.duplicadas + self.correctas + self.incorrectas)
        val += " (correctas={} incorrectas={}".format(self.correctas, self.incorrectas)
        if self.duplicadas > 0:
            val += " duplicadas={}".format(self.duplicadas)
        if self.ignoradas > 0:
            val += " ignoradas={}".format(self.ignoradas)
        val += ")"
        return val

    def resultado_metricas2(self):
        return "precision={:.2f}  recall={:.2f}  F1={:.2f}".format(self.precision, self.recall, self.f1)


class Evaluacion:
    def __init__(self, ground_truth):
        self.ground_truth = ground_truth
        self.lista_ignoradas = list()
        self.lista_duplicadas = list()
        self.lista_correctas = list()
        self.lista_incorrectas = list()
        self.correctas_por_tipo = dict()
        self.current_threshold = None
        self.queries = set()

    def evaluar(self, det, gt):
        self.current_threshold = det.distancia
        # no es un query con respuesta correcta
        if gt is None:
            det.linea += '\t(según GT es -)'
            self.lista_incorrectas.append(det)
            return
        # la tarea evalua solo la primera respuesta por query
        if det.imagen_q in self.queries:
            self.lista_duplicadas.append(det)
            return
        self.queries.add(det.imagen_q)
        # evaluar si la deteccion es correcta a no
        if gt.imagen_r == det.imagen_r:
            self.lista_correctas.append(det)
            if gt.tipo not in self.correctas_por_tipo:
                self.correctas_por_tipo[gt.tipo] = list()
            self.correctas_por_tipo[gt.tipo].append(det)
        else:
            det.linea += '\t(según GT es ' + gt.imagen_r + ') (tipo=' + gt.tipo + ')'
            self.lista_incorrectas.append(det)

    def calcular_metricas(self):
        m = Metricas()
        m.threshold = self.current_threshold
        m.ignoradas = len(self.lista_ignoradas)
        m.duplicadas = len(self.lista_duplicadas)
        m.correctas = len(self.lista_correctas)
        m.incorrectas = len(self.lista_incorrectas)
        m.num_queries = self.ground_truth.total_queries()
        m.precision = m.correctas / (m.correctas + m.incorrectas)
        m.recall = m.correctas / self.ground_truth.total_queries()
        if m.precision == 0 or m.recall == 0:
            m.f1 = 0
        else:
            m.f1 = 2 * m.precision * m.recall / (m.precision + m.recall)
        for tipo in self.ground_truth.total_por_tipo:
            total = self.ground_truth.total_por_tipo[tipo]
            correctas = 0
            if tipo in self.correctas_por_tipo:
                correctas = len(self.correctas_por_tipo[tipo])
            m.correcta_por_tipo[tipo] = correctas
            m.recall_por_tipo[tipo] = correctas / total
        return m


class Evaluador:
    def __init__(self, filename_ground_truth, filename_detecciones):
        self.ground_truth = GroudTruth()
        self.ground_truth.leer_archivo_gt(filename_ground_truth)
        self.detecciones = Detecciones()
        self.detecciones.leer_archivo_detecciones(filename_detecciones)
        self.mejor_precision = None
        self.mejor_f1 = None
        self.metricas = None
        self.ev = Evaluacion(self.ground_truth)

    def evaluar_detecciones(self):
        # ordenar detecciones por distancia
        self.detecciones.lista.sort(key=lambda x: x.distancia)
        # revisar cada deteccion
        for det in self.detecciones.lista:
            gt = self.ground_truth.buscar_gt(det.imagen_q)
            # evaluar si la deteccion es correcta a no
            self.ev.evaluar(det, gt)
            self.metricas = self.ev.calcular_metricas()
            # mantener el mejor resultado encontrado hasta el momento
            if self.mejor_precision is None or self.metricas.precision >= self.mejor_precision.precision:
                self.mejor_precision = self.metricas
            if self.mejor_f1 is None or self.metricas.f1 > self.mejor_f1.f1:
                self.mejor_f1 = self.metricas

    def imprimir_resultado(self):
        print()
        print("Resultado logrado = {} correctas de {} ({:.0f}%)".format(
            self.metricas.correctas, self.metricas.num_queries,
            100 * self.metricas.recall))
        nota_calidad = 7 * self.metricas.recall / 0.5
        if nota_calidad > 7:
            nota_calidad = 7
        elif nota_calidad < 1:
            nota_calidad = 1
        print("==> Nota calidad resultados = {:.1f}   (pondera 60% en nota final de la tarea)".format(nota_calidad))
        if self.metricas.recall > 0.5:
            print("==> Bonus = {:.1f} puntos para otra tarea o mini-control".format(4 * (self.metricas.recall - 0.5)))
        print()
        print("A continuación otros indicadores útiles:")
        print()
        print(self.metricas.resultado_por_tipo())

    def imprimir_incorrectas(self, incorrectas_a_mostrar):
        print()
        print("  Las primeras {} respuestas incorrectas:".format(incorrectas_a_mostrar))
        cont = 0
        for det in self.ev.lista_incorrectas:
            print("    {}".format(det.linea))
            cont += 1
            if cont == incorrectas_a_mostrar:
                break

    def imprimir_metricas(self):
        print()
        print("  Mejor Precision con:")
        print("    {}".format(self.mejor_precision.resultado_metricas1()))
        print("    {}".format(self.mejor_precision.resultado_metricas2()))
        print()
        print("  Mejor F1 con:")
        print("    {}".format(self.mejor_f1.resultado_metricas1()))
        print("    {}".format(self.mejor_f1.resultado_metricas2()))


def evaluar_resultados(resultados, filename_gt):
    print("Evaluando {} con {}".format(resultados, filename_gt));
    incorrectas_a_mostrar = 10
    evaluador = Evaluador(filename_gt, resultados)
    evaluador.evaluar_detecciones()
    evaluador.imprimir_resultado()
    evaluador.imprimir_incorrectas(incorrectas_a_mostrar)
    evaluador.imprimir_metricas()


def ejecutar_comandos(dataset_r, dataset_q, datos_r, resultados):
    # comando para tareas python
    comando1 = ["python", "tarea1-procesar.py", dataset_r, datos_r]
    comando2 = ["python", "tarea1-buscar.py", dataset_q, datos_r, resultados]
    # comando para tareas c++
    # comando1 = ["./tarea1-procesar", dataset_r, datos_r]
    # comando2 = ["./tarea1-buscar", dataset_q, datos_r, resultados]
    # comando para tareas java
    # comando1 = ["java", "tarea1-procesar", dataset_r, datos_r]
    # comando2 = ["java", "tarea1-buscar", dataset_q, datos_r, resultados]

    print(comando1)
    code = subprocess.call(comando1)
    if code != 0:
        print("ERROR!")
        sys.exit()

    print(comando2)
    code = subprocess.call(comando2)
    if code != 0:
        print("ERROR!")
        sys.exit()


# inicio
if len(sys.argv) < 3:
    print("CC5213 - Evaluación Tarea 1  (2020-2)")
    print("Uso: {} [datasets_base_dir] [nombre dataset: a,b,c]".format(sys.argv[0]))
    sys.exit(1)

datasets_base_dir = sys.argv[1]
name = sys.argv[2]

dataset_q = "{}/dataset_q_{}".format(datasets_base_dir, name)
dataset_r = "{}/dataset_r_{}".format(datasets_base_dir, name)
filename_gt = "{}/dataset_gt_{}.txt".format(datasets_base_dir, name)

datos_r = "datos_{}_r".format(name)
resultados = "resultados_{}.txt".format(name)

ejecutar_comandos(dataset_r, dataset_q, datos_r, resultados)

evaluar_resultados(resultados, filename_gt)
