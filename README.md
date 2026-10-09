# 📊 Analista de CSV

Agente de IA para la terminal que analiza archivos CSV conversando en lenguaje natural. Usa **Gemini** como modelo, **LangChain** para el agente y la memoria, y un **servidor MCP local** que ofrece las herramientas de análisis con **pandas**. Está construido con una **arquitectura hexagonal ligera** y especificado con un SDD.

## ✨ Qué demuestra

| Concepto | Dónde se ve |
|---|---|
| **Gemini** genera las respuestas | `ChatGoogleGenerativeAI` en `agente_csv.py` |
| **LangChain** conecta el agente | `create_agent(...)` |
| **MCP**: las Tools viven en un servidor aparte | `servidor.py` + `adaptadores/entrada/servidor_mcp.py` |
| **Memoria** de la conversación | `InMemorySaver` + `thread_id` |
| **Arquitectura hexagonal** | carpetas `dominio/`, `aplicacion/`, `adaptadores/` |
| **Pruebas sin Gemini ni MCP** | `tests/` con un repositorio falso en memoria |
| **SDD** (especificación primero) | `docs/SDD.md` |

## 🧠 Cómo funciona

```text
Tú → agente_csv.py (Gemini + LangChain + memoria)
          ↓  MCP (stdio)
     servidor.py  →  Adaptador MCP → Servicio de análisis → Puerto → Adaptador CSV (pandas) → data/*.csv
```

**El agente decide; el servidor ejecuta.** El servidor no usa Gemini ni tiene memoria: solo ofrece funciones de análisis.

## 🛠️ Tools

| Tool | Qué hace |
|---|---|
| `listar_csv` | Lista los CSV disponibles en `data/` |
| `describir_csv` | Filas, columnas, tipos, nulos y las primeras 5 filas |
| `filtrar_filas` | Filas que cumplen una condición (`==`, `!=`, `>`, `>=`, `<`, `<=`, `contiene`) |
| `top_n` | Las N filas con mayor o menor valor de una columna numérica |
| `promedio_columna` | Promedio de una columna numérica, ignorando nulos |

## 🏛️ Arquitectura hexagonal

Las dependencias apuntan siempre **hacia adentro**: `adaptadores → aplicacion → dominio`.

```text
analista-csv/
├── data/                         # ÚNICA carpeta desde la que se leen CSV
│   └── ventas.csv                # datos de ejemplo (inventados)
├── dominio/
│   └── errores.py                # errores de negocio
├── aplicacion/
│   ├── puertos.py                # puerto: RepositorioDatasets
│   └── servicio_analisis.py      # casos de uso
├── adaptadores/
│   ├── entrada/servidor_mcp.py   # Tools MCP (FastMCP)
│   └── salida/repositorio_csv.py # lectura segura de CSV con pandas
├── tests/                        # pruebas con pytest
├── config.py                     # carpeta de datos y máximo de filas
├── servidor.py                   # raíz de composición: ensambla y arranca el servidor
├── agente_csv.py                 # agente cliente (Gemini + memoria)
├── probar_servidor.py            # prueba manual del servidor, sin Gemini
└── docs/SDD.md                   # especificación: requisitos funcionales y no funcionales
```

- `dominio/` y `aplicacion/` **no importan** MCP ni LangChain.
- Cambiar la entrada (MCP por una CLI) o la salida (CSV por Excel) no toca la lógica de análisis.

## ✅ Requisitos

- Python 3.10 o superior
- Una API key de Gemini, gratuita en [Google AI Studio](https://aistudio.google.com)

## 🚀 Instalación

```powershell
# 1. Clonar
git clone <URL-DE-TU-REPOSITORIO>
cd analista-csv

# 2. Entorno virtual
python -m venv venv
venv\Scripts\Activate.ps1          # Mac/Linux: source venv/bin/activate

# 3. Dependencias
python -m pip install -r requirements.txt
```

> `mcp` se fija en una versión menor a 2 porque `langchain-mcp-adapters` aún no es compatible con `mcp` 2.x.

## 🔑 Configuración

Copia `.env.example` como `.env` y escribe tu clave:

```text
GOOGLE_API_KEY=tu_api_key_aqui
```

Opcionalmente puedes elegir el modelo con `GEMINI_MODEL=nombre-del-modelo`. Los modelos del nivel gratuito cambian con el tiempo.

## ▶️ Uso

```powershell
python agente_csv.py
```

No hace falta iniciar el servidor aparte: el agente lo lanza solo. Escribe `salir` para terminar.

### Preguntas de ejemplo

```text
¿Qué archivos tengo?
Descríbeme ventas.csv
¿Cuál es el promedio de unidades?
Los 3 productos con mayor total
Muéstrame las ventas de la región Norte
¿Qué es un promedio?
```

Cada vez que el agente usa una Tool se muestra una línea `🔧 Tool usada: ...` con sus argumentos.

## 🧪 Pruebas

```powershell
python -m pytest            # lógica y seguridad; no necesita Gemini ni internet
python probar_servidor.py   # comprueba el servidor MCP con un cliente mínimo
```

## 🔒 Seguridad

- Solo se leen archivos `.csv` dentro de `data/`: se rechazan rutas absolutas, con `..` y subcarpetas.
- Todas las Tools son de **solo lectura**.
- Ninguna Tool devuelve más de 20 filas.
- La API key vive en `.env`, que no se sube al repositorio.

## ⚠️ Limitaciones

- La memoria vive en RAM: se borra al cerrar el programa.
- Analiza un archivo a la vez (sin combinar archivos).
- **Lo que devuelven las Tools viaja a Gemini.** Usa solo datos no sensibles. El nivel gratuito puede usar las entradas para mejorar los productos de Google.
- El nivel gratuito de Gemini puede responder con errores `503` (saturación) o `504` (tiempo de espera); basta con repetir la pregunta.

## 🔭 Próximos pasos

- Búsqueda web con DuckDuckGo mediante un segundo servidor MCP.
- Despliegue del servidor MCP en la nube (transporte HTTP con token).

## 🧰 Tecnologías

Python · Gemini API · LangChain · MCP (SDK oficial, FastMCP) · pandas · pytest · python-dotenv

---

Proyecto académico para aprender agentes de IA, MCP y arquitectura de software.