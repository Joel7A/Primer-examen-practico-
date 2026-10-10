import csv
import mysql.connector
from mysql.connector import Error
from datetime import datetime


def ejecutar_etl_almacen():

    conexion = None
    cursor = None

    try:
        # Conexion a la base de datos MySQL
        conexion = mysql.connector.connect(
            host="localhost", database="almacen_db", user="root", password=""
        )

        if conexion.is_connected():
            cursor = conexion.cursor()

            # Crear la tabla si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_ventas (
                    id_transaccion INT PRIMARY KEY,
                    producto VARCHAR(150) NOT NULL,
                    cantidad INT NOT NULL,
                    precio_unitario DECIMAL(10,2) NOT NULL,
                    fecha_registro DATE NOT NULL,
                    correo_empleado VARCHAR(150),
                    total_venta DECIMAL(12,2) NOT NULL
                )
            """)

            print("Conectado a MySQL")
            print("Tabla historial_ventas preparada")

            registros_exitosos = 0
            registros_fallidos = 0
            registros_duplicados = 0

            datos_transformados = []
            ids_procesados = set()

            # 1 ----- EXTRACCION
            try:
                with open(
                    "transacciones_almacen.csv",
                    mode="r",
                    encoding="utf-8-sig",
                    newline="",
                ) as archivo_csv:
                    lector_csv = csv.DictReader(archivo_csv)

                    columnas_requeridas = {
                        "id_transaccion",
                        "producto",
                        "cantidad",
                        "precio_unitario",
                        "fecha_registro",
                        "correo_empleado",
                    }

                    if not columnas_requeridas.issubset(
                        set(lector_csv.fieldnames or [])
                    ):
                        raise ValueError(
                            "El CSV no contiene todas las columnas requeridas."
                        )

                    # 2 ----- TRANSFORMACION
                    for fila in lector_csv:
                        try:
                            # normalizacion
                            id_texto = (fila["id_transaccion"] or "").strip()
                            producto = (fila["producto"] or "").strip().upper()
                            cantidad_texto = (fila["cantidad"] or "").strip()
                            precio_texto = (fila["precio_unitario"] or "").strip()
                            fecha_texto = (fila["fecha_registro"] or "").strip()
                            correo = (fila["correo_empleado"] or "").strip().lower()

                            # Validacion de campos
                            if not id_texto or not producto:
                                registros_fallidos += 1
                                continue

                            if not cantidad_texto or not precio_texto:
                                registros_fallidos += 1
                                continue

                            if not fecha_texto:
                                registros_fallidos += 1
                                continue

                            # Convertir tipos de datos
                            id_transaccion = int(id_texto)
                            cantidad = int(cantidad_texto)
                            precio_unitario = float(precio_texto)

                            # Validar cantidad y precio
                            if cantidad <= 0 or precio_unitario <= 0:
                                registros_fallidos += 1
                                continue

                            # Evitar ids duplicados
                            if id_transaccion in ids_procesados:
                                registros_duplicados += 1
                                continue

                            # Normalizar fechas con los formatos del CSV
                            formatos_fecha = (
                                "%Y-%m-%d",
                                "%Y/%m/%d",
                                "%d-%m-%Y",
                                "%d/%m/%Y",
                            )

                            fecha_registro = None

                            for formato in formatos_fecha:
                                try:
                                    fecha_registro = datetime.strptime(
                                        fecha_texto, formato
                                    ).date()
                                    break
                                except ValueError:
                                    continue

                            if fecha_registro is None:
                                registros_fallidos += 1
                                continue

                            # Calcular total de venta
                            total_venta = cantidad * precio_unitario

                            # Preparar registro para la carga masiva
                            datos_transformados.append(
                                (
                                    id_transaccion,
                                    producto,
                                    cantidad,
                                    precio_unitario,
                                    fecha_registro,
                                    correo,
                                    total_venta,
                                )
                            )

                            ids_procesados.add(id_transaccion)

                        except (ValueError, TypeError, KeyError):
                            registros_fallidos += 1
                            continue

            except (FileNotFoundError, OSError, csv.Error, ValueError) as e:
                print(f"Error durante la extraccion: {e}")
                return

            # 3 ----- CARGA
            query = """
                INSERT INTO historial_ventas (
                    id_transaccion,
                    producto,
                    cantidad,
                    precio_unitario,
                    fecha_registro,
                    correo_empleado,
                    total_venta
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            try:
                cursor.executemany(query, datos_transformados)
                conexion.commit()

                registros_exitosos = len(datos_transformados)

            except Error as e:
                conexion.rollback()
                print(f"Error durante la carga. Se revirtieron los cambios: {e}")
                return

            print("\n----- RESUMEN DEL ETL -----")
            print(
                f"Registros leidos: {registros_exitosos + registros_fallidos + registros_duplicados}"
            )
            print(f"Registros cargados correctamente: {registros_exitosos}")
            print(f"Registros descartados por errores: {registros_fallidos}")
            print(f"Registros duplicados descartados: {registros_duplicados}")

    except Error as e:
        print(f"Error de conexion o base de datos: {e}")

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()

        print("Conexion a MySQL cerrada.")


ejecutar_etl_almacen()
