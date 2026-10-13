import mysql.connector
from mysql.connector import Error


class Cargador:
    def cargar(self, datos_transformados):
        conexion = None
        cursor = None
        try:
            # conexion a la base de datos
            conexion = mysql.connector.connect(
                host="localhost", database="almacen_db", user="root", password=""
            )

            cursor = conexion.cursor()

            # creacion de la tabla de la BBDD
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_ventas (
                    id_transaccion INT PRIMARY KEY,
                    producto VARCHAR(150) NOT NULL,
                    cantidad INT NOT NULL,
                    precio_unitario DECIMAL(10,2) NOT NULL,
                    fecha_registro DATE NOT NULL, 
                    correo_empleado VARCHAR(150) NOT NULL,
                    total_venta DECIMAL(10,2) NOT NULL
                )
                """)

            # si falla datos_transformados
            if not datos_transformados:
                print("no hay registros validos para cargar'")
                conexion.commit()
                return

            # Insercion de datos transformados
            consultaSQL = """
                INSERT INTO historial_ventas(
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

            cursor.executemany(consultaSQL, datos_transformados)

            conexion.commit()

            print(f"Registros cargados: {cursor.rowcount}")
        except Error:
            if conexion is not None and conexion.is_connected():
                conexion.rollback()
                print("Error al cargar los registros en la base de datos")
            raise
        finally:
            if cursor is not None:
                cursor.close()
            if conexion is not None and conexion.is_connected():
                conexion.close()
