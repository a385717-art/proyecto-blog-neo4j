"""Conexión compartida y ejecución de consultas Cypher."""

from config import Config
from neo4j import GraphDatabase


class Neo4jConnection:
    """Mantiene el controlador y ejecuta consultas en la base configurada."""

    def __init__(self):
        self._driver = GraphDatabase.driver(
            Config.NEO4J_URI, auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD),
            # para que la ventana no se trabe tanto si se cae el internet
            max_transaction_retry_time=5, connection_timeout=10,
        )

    def close(self):
        """Libera los recursos del controlador al terminar la aplicación."""
        if self._driver is not None:
            self._driver.close()

    def verify(self):
        # revisa que se pueda conectar, sin reintentos para fallar rápido
        self._driver.verify_connectivity()

    def query(self, cypher_query, parameters=None):
        """Ejecuta Cypher con parámetros y devuelve la lista de registros."""
        records, summary, keys = self._driver.execute_query(
            cypher_query,
            parameters_=parameters or {},
            database_=Config.NEO4J_DATABASE,
        )
        return records


# Los módulos CRUD comparten este controlador.
db = Neo4jConnection()
