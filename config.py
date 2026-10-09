from pathlib import Path

# Carpeta del proyecto: donde vive este archivo
RAIZ = Path(__file__).resolve().parent

# ÚNICA carpeta desde la que se pueden leer CSV
RUTA_DATOS = RAIZ / "data"

# Máximo de filas que cualquier Tool puede devolver (RNF-05)
MAX_FILAS = 20