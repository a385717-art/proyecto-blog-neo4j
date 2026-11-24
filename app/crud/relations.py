"""Relaciones entre los nodos del blog: autor, comentarios, etiquetas y categorías."""

from database import db


def linkArticleAuthor(email: str, title: str, date: str) -> bool:
    """Pone al usuario como autor del artículo.

    Si el artículo ya tenía otro autor se le quita, porque solo puede tener uno.
    Devuelve False si no existe el usuario o el artículo.
    """
    query = """
    MATCH (u:User {email: $email})
    MATCH (a:Article {title: $title, date: date($date)})
    OPTIONAL MATCH (other:User)-[old:WROTE]->(a)
    WHERE other <> u
    DELETE old
    WITH DISTINCT u, a
    MERGE (u)-[:WROTE]->(a)
    RETURN count(*) AS linked
    """
    records = db.query(query, {"email": email, "title": title, "date": date})
    return records[0]["linked"] > 0


def addComment(email: str, title: str, date: str, name: str, url: str):
    """Crea el comentario ligado a su usuario y a su artículo.

    Devuelve el nodo o None si no existe el usuario o el artículo.
    """
    query = """
    MATCH (u:User {email: $email})
    MATCH (a:Article {title: $title, date: date($date)})
    CREATE (u)-[:WROTE]->(c:Comment {name: $name, url: $url})<-[:HAS_COMMENT]-(a)
    RETURN c
    """
    records = db.query(
        query,
        {"email": email, "title": title, "date": date, "name": name, "url": url},
    )
    return records[0]["c"] if records else None


def addTagToArticle(name: str, title: str, date: str) -> bool:
    """Liga la etiqueta al artículo. Devuelve False si alguno no existe."""
    query = """
    MATCH (t:Tag {name: $name})
    MATCH (a:Article {title: $title, date: date($date)})
    MERGE (a)-[:HAS_TAG]->(t)
    RETURN count(*) AS linked
    """
    records = db.query(query, {"name": name, "title": title, "date": date})
    return records[0]["linked"] > 0


def removeTagFromArticle(name: str, title: str, date: str) -> bool:
    """Quita la etiqueta del artículo. Devuelve False si no estaban ligados."""
    query = """
    MATCH (a:Article {title: $title, date: date($date)})-[r:HAS_TAG]->(t:Tag {name: $name})
    DELETE r
    RETURN count(*) AS removed
    """
    records = db.query(query, {"name": name, "title": title, "date": date})
    return records[0]["removed"] > 0


def addCategoryToArticle(name: str, title: str, date: str) -> bool:
    """Liga la categoría al artículo. Devuelve False si alguno no existe."""
    query = """
    MATCH (c:Category {name: $name})
    MATCH (a:Article {title: $title, date: date($date)})
    MERGE (a)-[:IN_CATEGORY]->(c)
    RETURN count(*) AS linked
    """
    records = db.query(query, {"name": name, "title": title, "date": date})
    return records[0]["linked"] > 0


def removeCategoryFromArticle(name: str, title: str, date: str) -> bool:
    """Quita la categoría del artículo. Devuelve False si no estaban ligados."""
    query = """
    MATCH (a:Article {title: $title, date: date($date)})-[r:IN_CATEGORY]->(c:Category {name: $name})
    DELETE r
    RETURN count(*) AS removed
    """
    records = db.query(query, {"name": name, "title": title, "date": date})
    return records[0]["removed"] > 0


def getArticleDetail(title: str, date: str):
    """Devuelve un diccionario con el artículo, su autor, etiquetas, categorías y comentarios.

    Devuelve None si el artículo no existe.
    """
    query = """
    MATCH (a:Article {title: $title, date: date($date)})
    OPTIONAL MATCH (u:User)-[:WROTE]->(a)
    RETURN a, u,
        [(a)-[:HAS_TAG]->(t:Tag) | t.name] AS tags,
        [(a)-[:IN_CATEGORY]->(c:Category) | c.name] AS categories,
        [(a)-[:HAS_COMMENT]->(c:Comment) | {
            name: c.name,
            url: c.url,
            author: head([(c)<-[:WROTE]-(cu:User) | cu.name])
        }] AS comments
    """
    records = db.query(query, {"title": title, "date": date})
    if not records:
        return None

    record = records[0]
    article = record["a"]
    author = record["u"]
    return {
        "title": article["title"],
        "date": article["date"].iso_format(),
        "text": article["text"],
        "author": {"name": author["name"], "email": author["email"]} if author else None,
        "tags": sorted(record["tags"]),
        "categories": sorted(record["categories"]),
        "comments": sorted(record["comments"], key=lambda c: (c["name"], c["url"])),
    }


def getArticlesByUser(email: str):
    """Devuelve los artículos que escribió el usuario, del más nuevo al más viejo."""
    query = """
    MATCH (:User {email: $email})-[:WROTE]->(a:Article)
    RETURN a
    ORDER BY a.date DESC, a.title
    """
    return [record["a"] for record in db.query(query, {"email": email})]


def getArticlesByTag(name: str):
    """Devuelve los artículos que tienen la etiqueta."""
    query = """
    MATCH (a:Article)-[:HAS_TAG]->(:Tag {name: $name})
    RETURN a
    ORDER BY a.date DESC, a.title
    """
    return [record["a"] for record in db.query(query, {"name": name})]


def getArticlesByCategory(name: str):
    """Devuelve los artículos que están en la categoría."""
    query = """
    MATCH (a:Article)-[:IN_CATEGORY]->(:Category {name: $name})
    RETURN a
    ORDER BY a.date DESC, a.title
    """
    return [record["a"] for record in db.query(query, {"name": name})]


def getCommentsByArticle(title: str, date: str):
    """Devuelve los comentarios del artículo ordenados por nombre y URL."""
    query = """
    MATCH (:Article {title: $title, date: date($date)})-[:HAS_COMMENT]->(c:Comment)
    RETURN c
    ORDER BY c.name, c.url
    """
    return [record["c"] for record in db.query(query, {"title": title, "date": date})]
