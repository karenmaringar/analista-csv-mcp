import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

RUTA_SERVIDOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "servidor.py")


async def llamar(sesion, etiqueta, tool, argumentos):
    resultado = await sesion.call_tool(tool, argumentos)
    print(f"{etiqueta}\n{resultado.content[0].text}\n")


async def main():
    params = StdioServerParameters(command=sys.executable, args=[RUTA_SERVIDOR])
    async with stdio_client(params) as (leer, escribir):
        async with ClientSession(leer, escribir) as sesion:
            await sesion.initialize()

            tools = await sesion.list_tools()
            print("Tools:", [t.name for t in tools.tools], "\n")

            await llamar(sesion, "1) listar_csv", "listar_csv", {})
            await llamar(sesion, "2) promedio de unidades", "promedio_columna",
                         {"archivo": "ventas.csv", "columna": "unidades"})
            await llamar(sesion, "3) ruta prohibida", "describir_csv",
                         {"archivo": "../.env"})
            await llamar(sesion, "4) promedio de una columna de texto", "promedio_columna",
                         {"archivo": "ventas.csv", "columna": "producto"})
            await llamar(sesion, "5) operador inválido", "filtrar_filas",
                         {"archivo": "ventas.csv", "columna": "unidades", "operador": "~", "valor": "5"})
            await llamar(sesion, "6) ¿el servidor sigue vivo?", "listar_csv", {})


asyncio.run(main())