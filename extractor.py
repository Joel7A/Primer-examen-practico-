import csv


class Extractor:
    def __init__(self, ruta_archivoP):
        self.ruta_archivo = ruta_archivoP

    def extraer(self):
        try:
            with open(
                self.ruta_archivo, "r", encoding="utf-8-sig", newline=""
            ) as archivoCSV:
                lector_csv = csv.DictReader(archivoCSV)

                registros = list(lector_csv)

                print(f"Registros extraidos{len(registros)}")

                return registros
        except (FileNotFoundError, OSError, csv.Error) as Error:
            print(f"no se mudo extraer los datos por: {Error}")
            raise
