from typing import Protocol

import pandas as pd


class RepositorioDatasets(Protocol):
    """Puerto de salida: lo que la aplicación necesita para obtener datos.

    No dice CÓMO se leen los datos (CSV, Excel, base de datos...).
    Solo dice QUÉ operaciones debe ofrecer quien los entregue.
    """

    def listar(self) -> list[str]:
        """Devuelve los nombres de los datasets disponibles."""
        ...

    def cargar(self, nombre: str) -> pd.DataFrame:
        """Devuelve un dataset como DataFrame de pandas."""
        ...