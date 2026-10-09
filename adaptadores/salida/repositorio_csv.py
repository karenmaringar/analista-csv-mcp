from pathlib import Path

import pandas as pd

from config import RUTA_DATOS
from dominio.errores import ArchivoNoEncontrado, ParametroInvalido, RutaNoPermitida


class RepositorioCsvLocal:
    """Adaptador de salida: implementa el puerto RepositorioDatasets leyendo CSV locales.

    Es de SOLO LECTURA y únicamente accede a la carpeta de datos.
    """

    def __init__(self, ruta_datos: Path = RUTA_DATOS):
        # La ruta se puede cambiar desde fuera: así las pruebas usan una carpeta temporal
        self._ruta_datos = Path(ruta_datos).resolve()

    def listar(self) -> list[str]:
        if not self._ruta_datos.is_dir():
            return []
        return sorted(p.name for p in self._ruta_datos.glob("*.csv") if p.is_file())

    def cargar(self, nombre: str) -> pd.DataFrame:
        ruta = self._resolver_ruta(nombre)
        try:
            return pd.read_csv(ruta, encoding="utf-8")
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
            raise ParametroInvalido(f"No pude leer '{nombre}' como un CSV válido.")

    def _resolver_ruta(self, nombre: str) -> Path:
        # Defensa 1: debe ser un nombre simple, sin carpetas ni separadores
        if not nombre or nombre != Path(nombre).name or "/" in nombre or "\\" in nombre:
            raise RutaNoPermitida(nombre)

        # Defensa 2: solo archivos .csv
        if not nombre.lower().endswith(".csv"):
            raise RutaNoPermitida(nombre)

        # Defensa 3: la ruta final debe quedar dentro de la carpeta de datos
        ruta = (self._ruta_datos / nombre).resolve()
        if ruta.parent != self._ruta_datos:
            raise RutaNoPermitida(nombre)

        if not ruta.is_file():
            raise ArchivoNoEncontrado(nombre)
        return ruta