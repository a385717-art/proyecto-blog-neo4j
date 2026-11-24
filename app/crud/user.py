"""Operaciones sobre nodos User, identificados por su correo."""

from database import db


def createUser(name: str, email: str):
    """Crea un usuario y devuelve el nodo creado."""
    query = """
    CREATE (u:User {name: $name, email: $email})
    RETURN u
    """
    records = db.query(query, {"name": name, "email": email})
    return records[0]["u"]


def getUsers():
    """Devuelve todos los usuarios como una lista de nodos."""
    query = """
    MATCH (u:User)
    RETURN u
    """
    return [record["u"] for record in db.query(query)]


def getUserByEmail(email: str):
    """Devuelve el usuario con ese correo o None si no existe."""
    query = """
    MATCH (u:User {email: $email})
    RETURN u
    """
    records = db.query(query, {"email": email})
    return records[0]["u"] if records else None


def updateUser(email: str, name: str):
    """Cambia el nombre del usuario o devuelve None si el correo no existe."""
    query = """
    MATCH (u:User {email: $email})
    SET u.name = $name
    RETURN u
    """
    records = db.query(query, {"email": email, "name": name})
    return records[0]["u"] if records else None


def deleteUser(email: str, detach: bool = False) -> bool:
    """Devuelve True si se borró el usuario y False si no existía.

    Sin detach Neo4j rechaza el borrado si el usuario tiene relaciones.
    Con detach=True se borran también sus relaciones.
    """
    if detach:
        query = """
        MATCH (u:User {email: $email})
        DETACH DELETE u
        RETURN count(*) AS deleted
        """
    else:
        query = """
        MATCH (u:User {email: $email})
        DELETE u
        RETURN count(*) AS deleted
        """
    records = db.query(query, {"email": email})
    return records[0]["deleted"] > 0
