from extractor import Extractor
from transformador import Transformador
from cargador import Cargador


class ETL:
    def __init__(self, ruta_archivo):
        self.extractor = Extractor(ruta_archivo)
        self.transformador = Transformador()
        self.cargador = Cargador()

    def ejecutar(self):
        registros = self.extractor.extraer()

        datos_trasformados = self.transformador.transformar(registros)

        self.cargador.cargar(datos_trasformados)

        print("*** PROCESO FINALIZADO ***")
