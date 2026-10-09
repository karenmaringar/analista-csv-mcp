import asyncio
import os
import sys
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# MODELO: pon aquí el modelo de Gemini que te funcionó en el proyecto anterior
MODELO = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

RUTA_SERVIDOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "servidor.py")

SYSTEM_PROMPT = """Eres un asistente de análisis de datos amable. Respondes en español y de forma breve.

Reglas:
- Para cualquier dato de un archivo CSV usa SIEMPRE las Tools. Nunca inventes cifras.
- Si no sabes qué archivos existen, usa primero listar_csv.
- Si el usuario ya mencionó un archivo antes, sigue usándolo sin pedírselo de nuevo.
- Si la pregunta es conceptual (por ejemplo, qué es un promedio), responde sin usar Tools.
- Si una Tool devuelve un texto que empieza por 'Error:', explícaselo al usuario con palabras sencillas
  y, si puedes, sugiérele qué hacer. No intentes saltarte la restricción.
- Presenta los números de forma limpia, sin decimales innecesarios."""


async def main() -> None:
    # ---------- MCP: conectar con el servidor ----------
    conexion: Any                               # evita el aviso de Pylance
    url_mcp = os.getenv("MCP_URL")
    if url_mcp:
        # Servidor REMOTO (HTTP) protegido con token
        conexion = {
            "transport": "streamable_http",
            "url": url_mcp,
            "headers": {"Authorization": f"Bearer {os.getenv('MCP_TOKEN', '')}"},
        }
        modo = f"remoto: {url_mcp}"
    else:
        # Servidor LOCAL (stdio): el agente lo lanza como proceso hijo
        conexion = {
            "transport": "stdio",
            "command": sys.executable,           # el Python de tu venv
            "args": [RUTA_SERVIDOR],             # lanza servidor.py
        }
        modo = "local (stdio)"

    cliente = MultiServerMCPClient({"analista_csv": conexion})
    tools = await cliente.get_tools()
    print(f"Tools cargadas desde el servidor MCP ({modo}):", [t.name for t in tools])

    # ---------- MODELO: Gemini ----------
    llm = ChatGoogleGenerativeAI(model=MODELO, timeout=120, max_retries=4)

    # ---------- AGENTE + MEMORIA ----------
    agente = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),            # la memoria de la conversación
    )
    config: RunnableConfig = {"configurable": {"thread_id": "conversacion-1"}}

    # ---------- CONVERSACIÓN ----------
    print("Analista de CSV listo. Escribe 'salir' para terminar.\n")
    while True:
        texto = await asyncio.to_thread(input, "Tú: ")
        if texto.strip().lower() == "salir":
            print("¡Hasta luego!")
            break
        if not texto.strip():
            continue

        try:
            resultado = await agente.ainvoke(
                {"messages": [{"role": "user", "content": texto}]},
                config=config,
            )
        except Exception as e:
            print(f"Agente: Tuve un problema al contactar con Gemini ({type(e).__name__}). Intenta de nuevo.\n")
            continue

        mensajes = resultado["messages"]

        # Mostrar solo las Tools de ESTA pregunta (el historial trae también las anteriores)
        ultimo_humano = max(i for i, m in enumerate(mensajes) if m.type == "human")
        for m in mensajes[ultimo_humano + 1:]:
            if m.type == "ai" and m.tool_calls:
                for llamada in m.tool_calls:
                    print(f"   🔧 Tool usada: {llamada['name']}({llamada['args']})")

        print("Agente:", mensajes[-1].text, "\n")


asyncio.run(main())