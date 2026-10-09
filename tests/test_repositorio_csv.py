import pytest

from adaptadores.salida.repositorio_csv import RepositorioCsvLocal
from dominio.errores import ArchivoNoEncontrado, RutaNoPermitida


@pytest.fixture
def repo(tmp_path):
    """Crea una carpeta temporal con un CSV y un TXT, y un repositorio que la usa."""
    (tmp_path / "ejemplo.csv").write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    (tmp_path / "notas.txt").write_text("hola", encoding="utf-8")
    return RepositorioCsvLocal(tmp_path)


def test_listar_solo_csv(repo):
    assert repo.listar() == ["ejemplo.csv"]


def test_cargar_csv_valido(repo):
    df = repo.cargar("ejemplo.csv")
    assert df.shape == (2, 2)


@pytest.mark.parametrize("nombre", [
    "../.env",
    "..\\.env",
    "C:\\Windows\\win.ini",
    "/etc/passwd",
    "sub/ejemplo.csv",
    "notas.txt",
    "ejemplo.csv.txt",
    "",
    "..",
])
def test_rutas_no_permitidas(repo, nombre):
    with pytest.raises(RutaNoPermitida):
        repo.cargar(nombre)


def test_archivo_inexistente(repo):
    with pytest.raises(ArchivoNoEncontrado):
        repo.cargar("no_existe.csv")
        