"""Punto de entrada: conecta a Neo4j y abre la ventana."""

import sys

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("No se encontró Tkinter. En Arch o CachyOS se instala con: sudo pacman -S tk")
    sys.exit(1)

try:
    from neo4j.exceptions import AuthError, ServiceUnavailable

    from config import Config
except ImportError as e:
    # falta instalar algo de requirements.txt
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Falta un paquete",
        f"No está instalado el paquete {e.name}.\nInstálalo con: pip install -r requirements.txt",
    )
    root.destroy()
    sys.exit(1)


def connectionError(error):
    # mensaje para cada tipo de falla al conectar
    if isinstance(error, AuthError):
        return "El usuario o la contraseña de Neo4j son incorrectos. Revisa el archivo .env."
    if isinstance(error, ServiceUnavailable):
        return "No se pudo llegar al servidor de Neo4j. Revisa la URI del .env y tu conexión a internet."
    if isinstance(error, ValueError):
        return "La URI de Neo4j no es válida. Revisa NEO4J_URI en el archivo .env."
    return f"No se pudo conectar a Neo4j:\n{error}"


def main():
    root = tk.Tk()
    root.withdraw()  # se esconde hasta saber si hay conexión

    if not (Config.NEO4J_URI and Config.NEO4J_USER and Config.NEO4J_PASSWORD):
        messagebox.showerror(
            "Falta configuración",
            "Faltan datos en el archivo .env (NEO4J_URI, NEO4J_USER o NEO4J_PASSWORD).",
        )
        root.destroy()
        return

    db = None
    try:
        from database import db

        db.verify()
    except Exception as e:
        messagebox.showerror("Error de conexión", connectionError(e))
        if db is not None:
            db.close()
        root.destroy()
        return

    try:
        from ui.menu import MainWindow

        MainWindow(root)
        root.deiconify()
        root.mainloop()
    finally:
        db.close()


if __name__ == "__main__":
    main()
