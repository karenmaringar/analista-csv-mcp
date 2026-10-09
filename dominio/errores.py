class ErrorDominio(Exception):
    """Base de todos los errores esperados del sistema.

    Quien use el servicio puede capturar esta clase para mostrar
    el mensaje al usuario, sin conocer cada error por separado.
    """


class RutaNoPermitida(ErrorDominio):
    def __init__(self, nombre: str):
        super().__init__(
            f"No puedo leer '{nombre}'. Solo puedo leer archivos .csv de la carpeta de datos."
        )


class ArchivoNoEncontrado(ErrorDominio):
    def __init__(self, nombre: str):
        super().__init__(f"No encontré el archivo '{nombre}'.")


class ColumnaNoExiste(ErrorDominio):
    def __init__(self, columna: str, disponibles: list[str]):
        lista = ", ".join(str(c) for c in disponibles)
        super().__init__(f"La columna '{columna}' no existe. Columnas disponibles: {lista}.")


class ColumnaNoNumerica(ErrorDominio):
    def __init__(self, columna: str):
        super().__init__(f"La columna '{columna}' no es numérica.")


class OperadorInvalido(ErrorDominio):
    def __init__(self, operador: str, validos: list[str]):
        lista = ", ".join(validos)
        super().__init__(f"El operador '{operador}' no es válido. Usa: {lista}.")


class ParametroInvalido(ErrorDominio):
    def __init__(self, mensaje: str):
        super().__init__(mensaje)