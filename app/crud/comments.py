"""Operaciones sobre comentarios. Cada comentario se identifica por su URL."""

from database import db


def createComment(name: str, url: str):
    """Crea el nodo y lo devuelve."""
    query = """
    CREATE (c:Comment {name: $name, url: $url})
    RETURN c
    """
    records = db.query(query, {"name": name, "url": url})
    return records[0]["c"]


def getComments():
    """Devuelve la lista de comentarios ordenada por nombre y URL."""
    query = """
    MATCH (c:Comment)
    RETURN c
    ORDER BY c.name, c.url
    """
    return [record["c"] for record in db.query(query)]


def getCommentByUrl(url: str):
    """Devuelve el nodo identificado por url o None si no existe."""
    query = """
    MATCH (c:Comment {url: $url})
    RETURN c
    """
    records = db.query(query, {"url": url})
    return records[0]["c"] if records else None


def updateComment(url: str, name: str, new_url: str):
    """Actualiza el nombre y la URL y devuelve el nodo o None si no existe."""
    query = """
    MATCH (c:Comment {url: $url})
    SET c.name = $name, c.url = $new_url
    RETURN c
    """
    records = db.query(query, {"url": url, "name": name, "new_url": new_url})
    return records[0]["c"] if records else None


def deleteComment(url: str) -> bool:
    """Devuelve True si se borró el nodo y False si no existía.

    Neo4j rechaza el borrado si el nodo tiene relaciones.
    """
    query = """
    MATCH (c:Comment {url: $url})
    DELETE c
    RETURN count(*) AS deleted
    """
    records = db.query(query, {"url": url})
    return records[0]["deleted"] > 0
