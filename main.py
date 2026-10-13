from etl_almacen import ETL


def main():
    proceso = ETL("./transacciones_almacen.csv")
    proceso.ejecutar()


if __name__ == "__main__":
    main()
