import pandas as pd
import pytest

from aplicacion.servicio_analisis import ServicioAnalisis
from dominio.errores import (
    ArchivoNoEncontrado,
    ColumnaNoExiste,
    ColumnaNoNumerica,
    OperadorInvalido,
    ParametroInvalido,
)


class RepositorioFalso:
    """Cumple el puerto RepositorioDatasets, pero con datos en memoria: sin archivos ni MCP."""

    def __init__(self, datasets: dict):
        self._datasets = datasets

    def listar(self) -> list[str]:
        return sorted(self._datasets)

    def cargar(self, nombre: str) -> pd.DataFrame:
        if nombre not in self._datasets:
            raise ArchivoNoEncontrado(nombre)
        return self._datasets[nombre].copy()


@pytest.fixture
def servicio():
    df = pd.DataFrame({
        "producto": ["Laptop", "Mouse", "Teclado", "Monitor", "Silla"],
        "region": ["Norte", "Sur", "Norte", "Centro", "Sur"],
        "unidades": [3, 20, None, 5, 4],            # un nulo; promedio de los 4 valores = 8.0
        "total": [2550.0, 300.0, 480.0, 1100.0, 480.0],
    })
    return ServicioAnalisis(RepositorioFalso({"ventas.csv": df}))


# ---------- listar y describir ----------

def test_listar_csv(servicio):
    assert "ventas.csv" in servicio.listar_csv()


def test_describir_csv(servicio):
    r = servicio.describir_csv("ventas.csv")
    assert "Filas: 5" in r
    assert "Columnas: 4" in r
    assert "unidades" in r
    assert "1 nulos" in r


# ---------- filtrar_filas ----------

def test_filtrar_texto_igual_sin_distinguir_mayusculas(servicio):
    r = servicio.filtrar_filas("ventas.csv", "region", "==", "norte")
    assert "Coincidencias: 2" in r


def test_filtrar_contiene(servicio):
    r = servicio.filtrar_filas("ventas.csv", "producto", "contiene", "LAP")
    assert "Coincidencias: 1" in r
    assert "Laptop" in r


@pytest.mark.parametrize("operador, valor, esperado", [
    ("==", "5", 1),
    ("!=", "5", 3),     # el nulo no cuenta
    (">", "5", 1),
    (">=", "5", 2),
    ("<", "5", 2),
    ("<=", "5", 3),
])
def test_filtrar_numerico(servicio, operador, valor, esperado):
    r = servicio.filtrar_filas("ventas.csv", "unidades", operador, valor)
    assert f"Coincidencias: {esperado}" in r


def test_filtrar_sin_coincidencias(servicio):
    r = servicio.filtrar_filas("ventas.csv", "unidades", ">", "100")
    assert "No hay filas" in r


def test_filtrar_respeta_limite(servicio):
    r = servicio.filtrar_filas("ventas.csv", "total", ">=", "0", limite=2)
    assert "Coincidencias: 5. Mostrando 2" in r


# ---------- top_n ----------

def test_top_n_mayor(servicio):
    r = servicio.top_n("ventas.csv", "total", 2)
    assert "Laptop" in r and "Monitor" in r
    assert "Mouse" not in r


def test_top_n_menor(servicio):
    r = servicio.top_n("ventas.csv", "total", 1, "menor")
    assert "Mouse" in r
    assert "Laptop" not in r


def test_top_n_recorta_al_maximo(servicio):
    r = servicio.top_n("ventas.csv", "total", 500)
    assert "recortado" in r


# ---------- promedio_columna ----------

def test_promedio_ignora_nulos(servicio):
    r = servicio.promedio_columna("ventas.csv", "unidades")
    assert "8.00" in r
    assert "4 valores" in r
    assert "1 nulos" in r


# ---------- errores ----------

def test_columna_inexistente(servicio):
    with pytest.raises(ColumnaNoExiste):
        servicio.promedio_columna("ventas.csv", "precio")


def test_promedio_columna_texto(servicio):
    with pytest.raises(ColumnaNoNumerica):
        servicio.promedio_columna("ventas.csv", "producto")


def test_operador_invalido(servicio):
    with pytest.raises(OperadorInvalido):
        servicio.filtrar_filas("ventas.csv", "unidades", "~", "5")


def test_contiene_en_columna_numerica(servicio):
    with pytest.raises(OperadorInvalido):
        servicio.filtrar_filas("ventas.csv", "unidades", "contiene", "5")


def test_n_invalido(servicio):
    with pytest.raises(ParametroInvalido):
        servicio.top_n("ventas.csv", "total", 0)


def test_valor_no_numerico(servicio):
    with pytest.raises(ParametroInvalido):
        servicio.filtrar_filas("ventas.csv", "unidades", "==", "abc")


def test_orden_invalido(servicio):
    with pytest.raises(ParametroInvalido):
        servicio.top_n("ventas.csv", "total", 3, "medio")


def test_archivo_inexistente(servicio):
    with pytest.raises(ArchivoNoEncontrado):
        servicio.describir_csv("otro.csv")