
import os

import uvicorn
from dotenv import load_dotenv

from adaptadores.entrada.servidor_mcp import crear_servidor
from adaptadores.salida.repositorio_csv import RepositorioCsvLocal
from aplicacion.servicio_analisis import ServicioAnalisis

load_dotenv()


def crear_app():
    # Construir el servicio de análisis CSV
    servicio = ServicioAnalisis(RepositorioCsvLocal())

    # Crear el servidor MCP para conexiones HTTP sin estado
    servidor = crear_servidor(
        servicio,
        host="0.0.0.0",
        stateless_http=True,
    )

    # Exponer el servidor sin exigir un token de autenticación
    return servidor.streamable_http_app()


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "8000"))
    uvicorn.run(crear_app(), host="0.0.0.0", port=puerto)