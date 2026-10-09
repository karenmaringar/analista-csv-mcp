import os
import secrets

import uvicorn
from dotenv import load_dotenv
from starlette.responses import JSONResponse

from adaptadores.entrada.servidor_mcp import crear_servidor
from adaptadores.salida.repositorio_csv import RepositorioCsvLocal
from aplicacion.servicio_analisis import ServicioAnalisis

load_dotenv()


class ExigirToken:
    """Middleware: rechaza con 401 toda petición que no traiga el token correcto."""

    def __init__(self, app, token: str):
        self.app = app
        self.esperado = b"Bearer " + token.encode()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            enviado = dict(scope["headers"]).get(b"authorization", b"")
            if not secrets.compare_digest(enviado, self.esperado):
                respuesta = JSONResponse({"error": "No autorizado"}, status_code=401)
                await respuesta(scope, receive, send)
                return
        await self.app(scope, receive, send)


def crear_app():
    token = os.getenv("MCP_TOKEN")
    if not token:
        raise SystemExit("Falta la variable de entorno MCP_TOKEN: el servidor no arranca sin ella.")

    # Raíz de composición (igual que servidor.py, pero con entrada HTTP)
    servicio = ServicioAnalisis(RepositorioCsvLocal())
    servidor = crear_servidor(servicio, host="0.0.0.0", stateless_http=True)
    return ExigirToken(servidor.streamable_http_app(), token)


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "8000"))        # Render define PORT automáticamente
    uvicorn.run(crear_app(), host="0.0.0.0", port=puerto)