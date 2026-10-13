from decimal import Decimal, InvalidOperation
from datetime import datetime


class Transformador:
    # formatos de fecha presentes en el cvs
    formatos_fecha = ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y")

    def transformar(self, registros):
        datos_transformados = []
        registros_fallidos = 0

        for registro in registros:
            try:
                # limpieza y conversion de dato
                id_transaccion = int(registro["id_transaccion"].strip())
                producto = registro["producto"].strip().upper()
                cantidad = int(registro["cantidad"].strip())
                precio_unitario = Decimal(registro["precio_unitario"].strip())
                fecha_texto = registro["fecha_registro"].strip()
                correo_empleado = registro["correo_empleado"].strip().lower()

                # validacion de los campos
                if not producto:
                    registros_fallidos += 1
                    continue

                if cantidad <= 0:
                    registros_fallidos += 1
                    continue

                if not precio_unitario.is_finite() or precio_unitario <= 0:
                    registros_fallidos += 1
                    continue

                if not fecha_texto:
                    registros_fallidos += 1
                    continue
                if not correo_empleado:
                    registros_fallidos += 1
                    continue

                # transfomacion de fecha
                fecha_registro = None
                for formato in self.formatos_fecha:
                    try:
                        fecha_registro = datetime.strptime(fecha_texto, formato).date()
                        break
                    except ValueError:
                        continue

                # descartar fechas que no coencidan con los formatos analiazados
                if fecha_registro is None:
                    registros_fallidos += 1
                    continue

                # operaciones
                precio_unitario = precio_unitario.quantize(Decimal("0.01"))

                total_venta = (precio_unitario * cantidad).quantize(Decimal("0.01"))

                # guardar los datos para su posterior carga
                datos_transformados.append(
                    (
                        id_transaccion,
                        producto,
                        cantidad,
                        precio_unitario,
                        fecha_registro,
                        correo_empleado,
                        total_venta,
                    )
                )

            except (
                ValueError,
                KeyError,
                TypeError,
                AttributeError,
                InvalidOperation,
            ):
                # print(f"Error: {e}") #si se quiere saber el tipo de error de debe de activar esta parte
                registros_fallidos += 1
                continue
        print(f"Registros transformados: {len(datos_transformados)}")
        print(f"Registros descartados: {registros_fallidos}")

        return datos_transformados
