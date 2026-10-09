from adaptadores.entrada.servidor_mcp import crear_servidor
from adaptadores.salida.repositorio_csv import RepositorioCsvLocal
from aplicacion.servicio_analisis import ServicioAnalisis


def main() -> None:
    # Raíz de composición: el ÚNICO archivo que conoce todas las piezas
    repositorio = RepositorioCsvLocal()            # adaptador de salida (lee los CSV)
    servicio = ServicioAnalisis(repositorio)       # casos de uso (el centro)
    servidor = crear_servidor(servicio)            # adaptador de entrada (MCP)
    servidor.run(transport="stdio")


if __name__ == "__main__":
    main()