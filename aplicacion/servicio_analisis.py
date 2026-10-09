import operator

import pandas as pd
from pandas.api.types import is_numeric_dtype

from aplicacion.puertos import RepositorioDatasets
from config import MAX_FILAS
from dominio.errores import (
    ColumnaNoExiste,
    ColumnaNoNumerica,
    OperadorInvalido,
    ParametroInvalido,
)

# Operadores admitidos y a qué función de Python corresponde cada uno
COMPARADORES = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}
OPERADORES_NUMERICOS = list(COMPARADORES)                 # ==, !=, >, >=, <, <=
OPERADORES_TEXTO = ["==", "!=", "contiene"]
OPERADORES = OPERADORES_NUMERICOS + ["contiene"]


class ServicioAnalisis:
    """Casos de uso del proyecto. Recibe un repositorio (el puerto) y no sabe de dónde vienen los datos.

    Todos los métodos devuelven texto en español, compacto, listo para que Gemini lo use.
    """

    def __init__(self, repositorio: RepositorioDatasets):
        self._repo = repositorio

    # ---------- casos de uso ----------

    def listar_csv(self) -> str:
        archivos = self._repo.listar()
        if not archivos:
            return "No hay archivos CSV disponibles."
        return "Archivos disponibles: " + ", ".join(archivos)

    def describir_csv(self, archivo: str) -> str:
        df = self._repo.cargar(archivo)
        lineas = [
            f"Archivo: {archivo}",
            f"Filas: {len(df)} | Columnas: {len(df.columns)}",
            "",
            "Columnas (tipo, nulos):",
        ]
        for col in df.columns:
            lineas.append(f"- {col} ({df[col].dtype}, {int(df[col].isna().sum())} nulos)")
        lineas += ["", "Primeras 5 filas:", df.head(5).to_string(index=False)]
        return "\n".join(lineas)

    def filtrar_filas(
        self, archivo: str, columna: str, operador: str, valor: str, limite: int = 10
    ) -> str:
        if operador not in OPERADORES:
            raise OperadorInvalido(operador, OPERADORES)
        self._validar_cantidad(limite, "limite")

        df = self._repo.cargar(archivo)
        self._validar_columna(df, columna)
        serie = df[columna]

        if is_numeric_dtype(serie):
            if operador not in OPERADORES_NUMERICOS:
                raise OperadorInvalido(operador, OPERADORES_NUMERICOS)
            mascara = COMPARADORES[operador](serie, self._a_numero(valor, columna))
        else:
            if operador not in OPERADORES_TEXTO:
                raise OperadorInvalido(operador, OPERADORES_TEXTO)
            texto = str(valor).strip().lower()
            serie_texto = serie.fillna("").astype(str).str.strip().str.lower()
            if operador == "==":
                mascara = serie_texto == texto
            elif operador == "!=":
                mascara = serie_texto != texto
            else:  # "contiene"
                mascara = serie_texto.str.contains(texto, regex=False)

        mascara = mascara & serie.notna()          # los nulos nunca cuentan como coincidencia
        total = int(mascara.sum())
        if total == 0:
            return f"No hay filas donde {columna} {operador} {valor}."

        efectivo, aviso = self._limitar(limite)
        filas = df[mascara].head(efectivo)
        return (
            f"Coincidencias: {total}. Mostrando {len(filas)}{aviso}:\n"
            + filas.to_string(index=False)
        )

    def top_n(self, archivo: str, columna: str, n: int = 5, orden: str = "mayor") -> str:
        if orden not in ("mayor", "menor"):
            raise ParametroInvalido("El parámetro 'orden' debe ser 'mayor' o 'menor'.")
        self._validar_cantidad(n, "n")

        df = self._repo.cargar(archivo)
        self._validar_numerica(df, columna)

        efectivo, aviso = self._limitar(n)
        datos = df.dropna(subset=[columna])         # los nulos no entran en el ranking
        if orden == "mayor":
            filas = datos.nlargest(efectivo, columna)
        else:
            filas = datos.nsmallest(efectivo, columna)
        return (
            f"{len(filas)} filas con {orden} valor en '{columna}'{aviso}:\n"
            + filas.to_string(index=False)
        )

    def promedio_columna(self, archivo: str, columna: str) -> str:
        df = self._repo.cargar(archivo)
        self._validar_numerica(df, columna)

        valores = df[columna].dropna()
        if valores.empty:
            raise ParametroInvalido(
                f"La columna '{columna}' no tiene valores para calcular el promedio."
            )
        nulos = int(df[columna].isna().sum())
        return (
            f"Promedio de '{columna}': {valores.mean():.2f} "
            f"(calculado con {len(valores)} valores; {nulos} nulos ignorados)."
        )

    # ---------- ayudas internas (validaciones) ----------

    @staticmethod
    def _validar_columna(df: pd.DataFrame, columna: str) -> None:
        if columna not in df.columns:
            raise ColumnaNoExiste(columna, list(df.columns))

    @classmethod
    def _validar_numerica(cls, df: pd.DataFrame, columna: str) -> None:
        cls._validar_columna(df, columna)
        if not is_numeric_dtype(df[columna]):
            raise ColumnaNoNumerica(columna)

    @staticmethod
    def _validar_cantidad(valor: int, nombre: str) -> None:
        if not isinstance(valor, int) or valor < 1:
            raise ParametroInvalido(f"El parámetro '{nombre}' debe ser un número entero mayor que 0.")

    @staticmethod
    def _limitar(cantidad: int) -> tuple[int, str]:
        """Aplica el máximo de filas (RNF-05) y devuelve el aviso si hubo recorte."""
        if cantidad > MAX_FILAS:
            return MAX_FILAS, f" (recortado al máximo de {MAX_FILAS} filas)"
        return cantidad, ""

    @staticmethod
    def _a_numero(valor: str, columna: str) -> float:
        try:
            return float(valor)
        except (TypeError, ValueError):
            raise ParametroInvalido(
                f"El valor '{valor}' no es un número, pero la columna '{columna}' es numérica."
            )