"""Operaciones sobre categorías. Cada categoría se identifica por su nombre."""

from database import db


def createCategory(name: str, url: str):
    """Crea el nodo y lo devuelve."""
    query = """
    CREATE (c:Category {name: $name, url: $url})
    RETURN c
    """
    records = db.query(query, {"name": name, "url": url})
    return records[0]["c"]


def getCategories():
    """Devuelve la lista de categorías ordenada por nombre."""
    query = """
    MATCH (c:Category)
    RETURN c
    ORDER BY c.name
    """
    return [record["c"] for record in db.query(query)]


def getCategoryByName(name: str):
    """Devuelve el nodo identificado por name o None si no existe."""
    query = """
    MATCH (c:Category {name: $name})
    RETURN c
    """
    records = db.query(query, {"name": name})
    return records[0]["c"] if records else None


def updateCategory(name: str, new_name: str, url: str):
    """Actualiza el nombre y la URL y devuelve el nodo o None si no existe."""
    query = """
    MATCH (c:Category {name: $name})
    SET c.name = $new_name, c.url = $url
    RETURN c
    """
    records = db.query(query, {"name": name, "new_name": new_name, "url": url})
    return records[0]["c"] if records else None


def deleteCategory(name: str, detach: bool = False) -> bool:
    """Devuelve True si se borró el nodo y False si no existía.

    Sin detach Neo4j rechaza el borrado si el nodo tiene relaciones.
    Con detach=True se borran también sus relaciones.
    """
    if detach:
        query = """
        MATCH (c:Category {name: $name})
        DETACH DELETE c
        RETURN count(*) AS deleted
        """
    else:
        query = """
        MATCH (c:Category {name: $name})
        DELETE c
        RETURN count(*) AS deleted
        """
    records = db.query(query, {"name": name})
    return records[0]["deleted"] > 0
