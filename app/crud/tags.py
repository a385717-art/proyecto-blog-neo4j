"""Operaciones sobre nodos Tag, identificados por su nombre."""

from database import db


def createTag(name: str, url: str | None = None):
    """Crea una etiqueta y devuelve el nodo creado."""
    query = """
    CREATE (t:Tag {name: $name})
    SET t.url = $url
    RETURN t
    """
    records = db.query(query, {"name": name, "url": url})
    return records[0]["t"]


def getTags():
    """Devuelve todas las etiquetas ordenadas por nombre."""
    query = """
    MATCH (t:Tag)
    RETURN t
    ORDER BY t.name
    """
    return [record["t"] for record in db.query(query)]


def getTagByName(name: str):
    """Devuelve la etiqueta con ese nombre o None si no existe."""
    query = """
    MATCH (t:Tag {name: $name})
    RETURN t
    """
    records = db.query(query, {"name": name})
    return records[0]["t"] if records else None


def updateTag(name: str, new_name: str, url: str | None = None):
    """Renombra el nodo y actualiza su URL si se indica.

    Devuelve la etiqueta actualizada o None si no existe.
    """
    query = """
    MATCH (t:Tag {name: $name})
    SET t.name = $new_name, t.url = coalesce($url, t.url)
    RETURN t
    """
    records = db.query(query, {"name": name, "new_name": new_name, "url": url})
    return records[0]["t"] if records else None


def deleteTag(name: str, detach: bool = False) -> bool:
    """Devuelve True si se borró la etiqueta y False si no existía.

    Sin detach Neo4j rechaza el borrado si la etiqueta tiene relaciones.
    Con detach=True se borran también sus relaciones.
    """
    if detach:
        query = """
        MATCH (t:Tag {name: $name})
        DETACH DELETE t
        RETURN count(*) AS deleted
        """
    else:
        query = """
        MATCH (t:Tag {name: $name})
        DELETE t
        RETURN count(*) AS deleted
        """
    records = db.query(query, {"name": name})
    return records[0]["deleted"] > 0
