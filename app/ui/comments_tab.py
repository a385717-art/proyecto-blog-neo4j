"""Pestaña de comentarios."""

import tkinter as tk
from tkinter import messagebox, ttk

from crud import addComment, deleteComment, getCommentsWithInfo, updateComment
from ui.common import articleOptions, checkFields, formatDate, showError, userOptions


class CommentsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.selected = None  # url del comentario seleccionado
        self.users = {}  # "Nombre (correo)" -> correo
        self.articles = {}  # "Título (fecha)" -> (título, fecha)

        # tabla
        columns = ("name", "url", "author", "article")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=15)
        self.table.heading("name", text="Comentario")
        self.table.heading("url", text="URL")
        self.table.heading("author", text="Autor")
        self.table.heading("article", text="Artículo")
        self.table.column("name", width=220)
        self.table.column("url", width=220)
        self.table.column("author", width=180)
        self.table.column("article", width=240)
        self.table.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")
        self.table.bind("<<TreeviewSelect>>", self.onSelect)

        # campos de captura
        form = ttk.Frame(self)
        form.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(form, text="Comentario:").grid(row=0, column=0, sticky="w")
        self.name = tk.StringVar()
        ttk.Entry(form, textvariable=self.name, width=50).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(form, text="URL:").grid(row=1, column=0, sticky="w")
        self.url = tk.StringVar()
        self.urlEntry = ttk.Entry(form, textvariable=self.url, width=50)
        self.urlEntry.grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(form, text="(la URL no se puede cambiar)").grid(row=1, column=2, sticky="w")
        ttk.Label(form, text="Autor:").grid(row=2, column=0, sticky="w")
        self.author = tk.StringVar()
        self.authorBox = ttk.Combobox(form, textvariable=self.author, state="readonly", width=48)
        self.authorBox.grid(row=2, column=1, sticky="w", padx=5)
        ttk.Label(form, text="Artículo:").grid(row=3, column=0, sticky="w")
        self.article = tk.StringVar()
        self.articleBox = ttk.Combobox(form, textvariable=self.article, state="readonly", width=48)
        self.articleBox.grid(row=3, column=1, sticky="w", padx=5)
        ttk.Label(form, text="(autor y artículo solo se eligen al crear)").grid(row=3, column=2, sticky="w")

        # botones
        buttons = ttk.Frame(self)
        buttons.grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Button(buttons, text="Crear", command=self.create).pack(side="left", padx=2)
        ttk.Button(buttons, text="Actualizar", command=self.update).pack(side="left", padx=2)
        ttk.Button(buttons, text="Borrar", command=self.delete).pack(side="left", padx=2)
        ttk.Button(buttons, text="Refrescar", command=self.refresh).pack(side="left", padx=2)
        ttk.Button(buttons, text="Limpiar", command=self.clear).pack(side="left", padx=2)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.refresh()

    def reloadOptions(self):
        # vuelve a cargar los usuarios y artículos de los combobox
        try:
            self.users = userOptions()
            self.articles = articleOptions()
        except Exception as e:
            showError(e)
            return
        self.authorBox["values"] = list(self.users)
        self.articleBox["values"] = list(self.articles)
        # si lo elegido ya no existe se limpia el combo
        # (con un comentario seleccionado los combos solo muestran sus datos)
        if not self.selected:
            if self.author.get() not in self.users:
                self.author.set("")
            if self.article.get() not in self.articles:
                self.article.set("")

    def refresh(self):
        self.table.delete(*self.table.get_children())
        try:
            comments = getCommentsWithInfo()
        except Exception as e:
            showError(e)
            return
        for c in comments:
            author = f"{c['author']} ({c['email']})" if c["email"] else "(sin autor)"
            article = f"{c['title']} ({formatDate(c['date'])})" if c["title"] else "(sin artículo)"
            self.table.insert("", "end", values=(c["name"], c["url"], author, article))
        self.reloadOptions()
        self.clear()

    def clear(self):
        self.selected = None
        self.table.selection_remove(self.table.selection())
        for var in (self.name, self.url, self.author, self.article):
            var.set("")
        self.urlEntry.state(["!disabled"])
        self.authorBox.state(["!disabled"])
        self.articleBox.state(["!disabled"])

    def onSelect(self, event):
        items = self.table.selection()
        if not items:
            return
        name, url, author, article = self.table.item(items[0], "values")
        self.selected = url
        self.name.set(name)
        self.url.set(url)
        self.author.set(author)
        self.article.set(article)
        # la URL es el identificador y el autor/artículo no se cambian al editar
        self.urlEntry.state(["disabled"])
        self.authorBox.state(["disabled"])
        self.articleBox.state(["disabled"])

    def create(self):
        if self.selected:
            messagebox.showinfo("Crear", "Primero presiona Limpiar para capturar un comentario nuevo.")
            return
        name = self.name.get().strip()
        url = self.url.get().strip()
        author = self.author.get()
        article = self.article.get()
        if not checkFields({"Comentario": name, "URL": url, "Autor": author, "Artículo": article}):
            return
        try:
            title, date = self.articles[article]
            comment = addComment(self.users[author], title, date, name, url)
        except KeyError:
            # el autor o el artículo se borró en otra pestaña
            messagebox.showerror("No encontrado", "El autor o el artículo ya no existen. Presiona Refrescar.")
            return
        except Exception as e:
            showError(e, duplicate=f"Ya existe un comentario con la URL {url}.")
            return
        if comment is None:
            messagebox.showerror("No encontrado", "El autor o el artículo ya no existen. Presiona Refrescar.")
        self.refresh()

    def update(self):
        if not self.selected:
            messagebox.showwarning("Actualizar", "Selecciona un comentario de la tabla.")
            return
        name = self.name.get().strip()
        if not checkFields({"Comentario": name}):
            return
        try:
            comment = updateComment(self.selected, name, self.selected)
        except Exception as e:
            showError(e)
            return
        if comment is None:
            messagebox.showerror("No encontrado", "Ese comentario ya no existe. Presiona Refrescar.")
        self.refresh()

    def delete(self):
        if not self.selected:
            messagebox.showwarning("Borrar", "Selecciona un comentario de la tabla.")
            return
        # un comentario siempre está ligado a su autor y su artículo,
        # así que se borra directo con sus relaciones
        if not messagebox.askyesno(
            "Borrar",
            f"¿Seguro que quieres borrar el comentario {self.selected}?\n"
            "También se quita de su autor y de su artículo.",
        ):
            return
        try:
            deleted = deleteComment(self.selected, detach=True)
        except Exception as e:
            showError(e)
            return
        if not deleted:
            messagebox.showerror("No encontrado", "Ese comentario ya no existe.")
        self.refresh()
