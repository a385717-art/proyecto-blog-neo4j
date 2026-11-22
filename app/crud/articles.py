"""Operaciones sobre artículos. La fecha se recibe en formato ISO (AAAA-MM-DD) y se guarda como DATE."""

from database import db


def createArticle(title: str, date: str, text: str):
    """Crea el nodo y lo devuelve."""
    query = """
    CREATE (a:Article {title: $title, date: date($date), text: $text})
    RETURN a
    """
    records = db.query(query, {"title": title, "date": date, "text": text})
    return records[0]["a"]


def getArticles():
    """Devuelve la lista de artículos ordenada por fecha descendente y título."""
    query = """
    MATCH (a:Article)
    RETURN a
    ORDER BY a.date DESC, a.title
    """
    return [record["a"] for record in db.query(query)]


def getArticleByTitleAndDate(title: str, date: str):
    """Devuelve el nodo identificado por title y date o None si no existe."""
    query = """
    MATCH (a:Article {title: $title, date: date($date)})
    RETURN a
    """
    records = db.query(query, {"title": title, "date": date})
    return records[0]["a"] if records else None


def updateArticle(
    title: str,
    date: str,
    text: str,
    new_title: str | None = None,
    new_date: str | None = None,
):
    """Actualiza el texto y, si se indican, el título y la fecha."""
    query = """
    MATCH (a:Article {title: $title, date: date($date)})
    SET a.text = $text,
        a.title = coalesce($new_title, a.title),
        a.date = coalesce(date($new_date), a.date)
    RETURN a
    """
    records = db.query(
        query,
        {
            "title": title,
            "date": date,
            "text": text,
            "new_title": new_title,
            "new_date": new_date,
        },
    )
    return records[0]["a"] if records else None


def deleteArticle(title: str, date: str) -> bool:
    """Devuelve True si se borró el nodo y False si no existía.

    Neo4j rechaza el borrado si el nodo tiene relaciones.
    """
    query = """
    MATCH (a:Article {title: $title, date: date($date)})
    DELETE a
    RETURN count(*) AS deleted
    """
    records = db.query(query, {"title": title, "date": date})
    return records[0]["deleted"] > 0
