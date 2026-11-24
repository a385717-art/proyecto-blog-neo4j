"""Funciones que usan todas las pestañas."""

import re
from datetime import date
from tkinter import messagebox

from neo4j.exceptions import (
    ConstraintError,
    CypherSyntaxError,
    Neo4jError,
    ServiceUnavailable,
    SessionExpired,
)

from crud import getArticles, getUsers


def formatDate(value):
    # Neo4j regresa la fecha como neo4j.time.Date, la pasamos a AAAA-MM-DD
    if value is None:
        return ""
    if hasattr(value, "iso_format"):
        return value.iso_format()
    return str(value)


def hasRelationsError(error):
    # Neo4j no deja borrar un nodo que todavía tiene relaciones
    return isinstance(error, ConstraintError) and "still has relationships" in error.message


def showError(error, duplicate="Ya existe un registro con ese identificador."):
    # Convierte los errores de Neo4j en un mensaje entendible
    if isinstance(error, ConstraintError) and "already exists" in error.message:
        messagebox.showerror("Dato repetido", duplicate)
    elif isinstance(error, CypherSyntaxError) and (
        "date" in (error.message or "").lower() or "valid values" in (error.message or "")
    ):
        messagebox.showerror("Fecha inválida", "La fecha no es válida. Usa el formato AAAA-MM-DD.")
    elif isinstance(error, (ServiceUnavailable, SessionExpired)):
        messagebox.showerror("Sin conexión", "Se perdió la conexión con Neo4j. Revisa tu internet.")
    elif isinstance(error, Neo4jError):
        messagebox.showerror("Error de Neo4j", error.message or str(error))
    else:
        messagebox.showerror("Error", str(error))


def checkFields(fields):
    # Recibe {"Nombre": valor, ...} y avisa si alguno viene vacío
    empty = [name for name, value in fields.items() if not value]
    if empty:
        messagebox.showwarning("Campos vacíos", "Llena estos campos: " + ", ".join(empty))
        return False
    return True


def checkDate(text):
    # La fecha tiene que venir como AAAA-MM-DD y ser un día que exista
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        messagebox.showwarning("Fecha inválida", "Escribe la fecha como AAAA-MM-DD, por ejemplo 2026-11-24.")
        return False
    try:
        date.fromisoformat(text)
    except ValueError:
        messagebox.showwarning("Fecha inválida", f"La fecha {text} no existe.")
        return False
    return True


def userOptions():
    # {"Nombre (correo)": correo} para los combobox de autor
    users = sorted(getUsers(), key=lambda u: (u["name"] or "").lower())
    return {f"{u['name']} ({u['email']})": u["email"] for u in users}


def articleOptions():
    # {"Título (AAAA-MM-DD)": (título, fecha)} para los combobox de artículo
    options = {}
    for a in getArticles():
        fecha = formatDate(a["date"])
        options[f"{a['title']} ({fecha})"] = (a["title"], fecha)
    return options
