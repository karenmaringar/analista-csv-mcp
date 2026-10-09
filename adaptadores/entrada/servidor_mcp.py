import logging

from mcp.server.fastmcp import FastMCP

from aplicacion.servicio_analisis import ServicioAnalisis
from dominio.errores import ErrorDominio


def crear_servidor(servicio: ServicioAnalisis) -> FastMCP:
    """Adaptador de entrada: expone los casos de uso del servicio como Tools MCP."""
    mcp = FastMCP("AnalistaCSV")

    def _ejecutar(accion) -> str:
        """Red de seguridad: convierte cualquier error en un texto, sin detener el servidor."""
        try:
            return accion()
        except ErrorDominio as e:
            return f"Error: {e}"               # error esperado: el mensaje ya es claro
        except Exception:
            logging.exception("Error inesperado en una Tool")   # va a stderr, no rompe el protocolo
            return "Error inesperado al procesar la solicitud. Intenta de nuevo."

    @mcp.tool()
    def listar_csv() -> str:
        """Lista los archivos CSV disponibles para analizar.
        Úsala primero cuando no sepas qué archivos existen."""
        return _ejecutar(servicio.listar_csv)

    @mcp.tool()
    def describir_csv(archivo: str) -> str:
        """Describe un archivo CSV: cantidad de filas y columnas, tipo de cada columna,
        nulos por columna y las primeras 5 filas. Úsala para conocer la estructura
        de un archivo antes de analizarlo.
        Parámetro: archivo (nombre del archivo, por ejemplo 'ventas.csv')."""
        return _ejecutar(lambda: servicio.describir_csv(archivo))

    @mcp.tool()
    def filtrar_filas(archivo: str, columna: str, operador: str, valor: str, limite: int = 10) -> str:
        """Devuelve las filas de un CSV que cumplen una condición sobre una columna.
        Operadores: ==, !=, >, >=, <, <= (columnas numéricas) y ==, !=, contiene (columnas de texto).
        Parámetros: archivo, columna, operador, valor (siempre como texto, por ejemplo '5' o 'Norte')
        y limite (máximo de filas a mostrar)."""
        return _ejecutar(lambda: servicio.filtrar_filas(archivo, columna, operador, valor, limite))

    @mcp.tool()
    def top_n(archivo: str, columna: str, n: int = 5, orden: str = "mayor") -> str:
        """Devuelve las N filas con el mayor o el menor valor de una columna numérica.
        Úsala para rankings. Parámetros: archivo, columna, n (cuántas filas)
        y orden ('mayor' o 'menor')."""
        return _ejecutar(lambda: servicio.top_n(archivo, columna, n, orden))

    @mcp.tool()
    def promedio_columna(archivo: str, columna: str) -> str:
        """Calcula el promedio de una columna numérica, ignorando los valores nulos.
        Parámetros: archivo y columna."""
        return _ejecutar(lambda: servicio.promedio_columna(archivo, columna))

    return mcp