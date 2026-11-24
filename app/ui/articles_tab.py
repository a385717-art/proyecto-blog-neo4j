"""Pestaña de artículos con su panel de detalle."""

import tkinter as tk
from tkinter import messagebox, ttk

from crud import (
    addCategoryToArticle,
    addComment,
    addTagToArticle,
    createArticle,
    deleteArticle,
    getArticleDetail,
    getArticles,
    getCategories,
    getTags,
    linkArticleAuthor,
    removeCategoryFromArticle,
    removeTagFromArticle,
    updateArticle,
)
from ui.common import (
    checkDate,
    checkFields,
    formatDate,
    hasRelationsError,
    showError,
    userOptions,
)


class ArticlesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.selected = None  # (título, fecha) del artículo seleccionado
        self.users = {}  # "Nombre (correo)" -> correo
        self.detail = None  # lo último que regresó getArticleDetail

        # a la izquierda la tabla y el formulario, a la derecha el detalle
        # (el divisor se puede arrastrar)
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)
        left = ttk.Frame(paned)
        right = ttk.LabelFrame(paned, text="Detalle del artículo", padding=8)
        paned.add(left, weight=3)
        paned.add(right, weight=2)

        # tabla
        self.table = ttk.Treeview(left, columns=("title", "date", "text"), show="headings", height=12)
        self.table.heading("title", text="Título")
        self.table.heading("date", text="Fecha")
        self.table.heading("text", text="Texto")
        self.table.column("title", width=200)
        self.table.column("date", width=90)
        self.table.column("text", width=220)
        self.table.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(left, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")
        self.table.bind("<<TreeviewSelect>>", self.onSelect)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        # campos de captura
        form = ttk.Frame(left)
        form.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(form, text="Título:").grid(row=0, column=0, sticky="w")
        self.title = tk.StringVar()
        self.titleEntry = ttk.Entry(form, textvariable=self.title, width=40)
        self.titleEntry.grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(form, text="Fecha:").grid(row=1, column=0, sticky="w")
        self.date = tk.StringVar()
        self.dateEntry = ttk.Entry(form, textvariable=self.date, width=12)
        self.dateEntry.grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(form, text="AAAA-MM-DD (título y fecha no se pueden cambiar)").grid(
            row=2, column=1, sticky="w", padx=5
        )
        ttk.Label(form, text="Texto:").grid(row=3, column=0, sticky="nw")
        self.text = tk.Text(form, width=50, height=4, wrap="word")
        self.text.grid(row=3, column=1, sticky="w", padx=5)

        # botones
        buttons = ttk.Frame(left)
        buttons.grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Button(buttons, text="Crear", command=self.create).pack(side="left", padx=2)
        ttk.Button(buttons, text="Actualizar", command=self.update).pack(side="left", padx=2)
        ttk.Button(buttons, text="Borrar", command=self.delete).pack(side="left", padx=2)
        ttk.Button(buttons, text="Refrescar", command=self.refresh).pack(side="left", padx=2)
        ttk.Button(buttons, text="Limpiar", command=self.clear).pack(side="left", padx=2)

        self.buildDetail(right)
        self.refresh()

    def buildDetail(self, panel):
        self.detailTitle = ttk.Label(panel, text="Selecciona un artículo", font=("", 10, "bold"))
        self.detailTitle.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        # autor
        ttk.Label(panel, text="Autor:").grid(row=1, column=0, sticky="nw")
        self.authorLabel = ttk.Label(panel, text="-", wraplength=260)
        self.authorLabel.grid(row=1, column=1, columnspan=2, sticky="w")
        self.author = tk.StringVar()
        self.authorBox = ttk.Combobox(panel, textvariable=self.author, state="readonly", width=30)
        self.authorBox.grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Button(panel, text="Asignar autor", command=self.assignAuthor).grid(row=2, column=2, sticky="w")

        # etiquetas
        ttk.Label(panel, text="Etiquetas:").grid(row=3, column=0, sticky="nw", pady=(8, 0))
        self.tagsLabel = ttk.Label(panel, text="-", wraplength=260)
        self.tagsLabel.grid(row=3, column=1, columnspan=2, sticky="w", pady=(8, 0))
        self.tag = tk.StringVar()
        self.tagBox = ttk.Combobox(panel, textvariable=self.tag, state="readonly", width=30)
        self.tagBox.grid(row=4, column=0, columnspan=2, sticky="w", pady=2)
        tagButtons = ttk.Frame(panel)
        tagButtons.grid(row=4, column=2, sticky="w")
        ttk.Button(tagButtons, text="Agregar", command=self.addTag).pack(side="left")
        ttk.Button(tagButtons, text="Quitar", command=self.removeTag).pack(side="left")

        # categorías
        ttk.Label(panel, text="Categorías:").grid(row=5, column=0, sticky="nw", pady=(8, 0))
        self.categoriesLabel = ttk.Label(panel, text="-", wraplength=260)
        self.categoriesLabel.grid(row=5, column=1, columnspan=2, sticky="w", pady=(8, 0))
        self.category = tk.StringVar()
        self.categoryBox = ttk.Combobox(panel, textvariable=self.category, state="readonly", width=30)
        self.categoryBox.grid(row=6, column=0, columnspan=2, sticky="w", pady=2)
        categoryButtons = ttk.Frame(panel)
        categoryButtons.grid(row=6, column=2, sticky="w")
        ttk.Button(categoryButtons, text="Agregar", command=self.addCategory).pack(side="left")
        ttk.Button(categoryButtons, text="Quitar", command=self.removeCategory).pack(side="left")

        # comentarios
        ttk.Label(panel, text="Comentarios:").grid(row=7, column=0, sticky="w", pady=(8, 2))
        self.commentsTable = ttk.Treeview(panel, columns=("name", "author"), show="headings", height=6)
        self.commentsTable.heading("name", text="Comentario")
        self.commentsTable.heading("author", text="Autor")
        self.commentsTable.column("name", width=220)
        self.commentsTable.column("author", width=120)
        self.commentsTable.grid(row=8, column=0, columnspan=3, sticky="nsew")
        ttk.Button(panel, text="Agregar comentario", command=self.openCommentDialog).grid(
            row=9, column=0, columnspan=3, sticky="w", pady=4
        )
        panel.rowconfigure(8, weight=1)

    # ---------- CRUD del artículo ----------

    def reloadOptions(self):
        # recarga los combobox y el detalle por si cambió algo en otra pestaña
        try:
            self.users = userOptions()
            tags = [t["name"] for t in getTags()]
            categories = [c["name"] for c in getCategories()]
        except Exception as e:
            showError(e)
            return
        self.authorBox["values"] = list(self.users)
        self.tagBox["values"] = tags
        self.categoryBox["values"] = categories
        self.showDetail()

    def refresh(self):
        self.table.delete(*self.table.get_children())
        try:
            articles = getArticles()  # ya vienen ordenados por fecha
        except Exception as e:
            showError(e)
            return
        for a in articles:
            preview = (a["text"] or "").replace("\n", " ")[:60]
            self.table.insert("", "end", values=(a["title"], formatDate(a["date"]), preview))
        self.clear()
        self.reloadOptions()

    def clear(self):
        self.selected = None
        self.table.selection_remove(self.table.selection())
        self.title.set("")
        self.date.set("")
        self.text.delete("1.0", "end")
        self.titleEntry.state(["!disabled"])
        self.dateEntry.state(["!disabled"])
        self.showDetail()

    def onSelect(self, event):
        items = self.table.selection()
        if not items:
            return
        title, date = self.table.item(items[0], "values")[:2]
        self.selected = (title, date)
        self.title.set(title)
        self.date.set(date)
        # título y fecha son el identificador, por eso se bloquean
        self.titleEntry.state(["disabled"])
        self.dateEntry.state(["disabled"])
        self.showDetail()
        # la tabla solo trae un pedazo del texto, el completo viene del detalle
        self.text.delete("1.0", "end")
        if self.detail:
            self.text.insert("1.0", self.detail["text"] or "")

    def create(self):
        if self.selected:
            messagebox.showinfo("Crear", "Primero presiona Limpiar para capturar un artículo nuevo.")
            return
        title = self.title.get().strip()
        date = self.date.get().strip()
        text = self.text.get("1.0", "end").strip()
        if not checkFields({"Título": title, "Fecha": date, "Texto": text}):
            return
        if not checkDate(date):
            return
        try:
            createArticle(title, date, text)
        except Exception as e:
            showError(e, duplicate=f"Ya existe un artículo {title} con fecha {date}.")
            return
        self.refresh()

    def update(self):
        if not self.selected:
            messagebox.showwarning("Actualizar", "Selecciona un artículo de la tabla.")
            return
        text = self.text.get("1.0", "end").strip()
        if not checkFields({"Texto": text}):
            return
        title, date = self.selected
        try:
            article = updateArticle(title, date, text)
        except Exception as e:
            showError(e)
            return
        if article is None:
            messagebox.showerror("No encontrado", "Ese artículo ya no existe. Presiona Refrescar.")
        self.refresh()

    def delete(self):
        if not self.selected:
            messagebox.showwarning("Borrar", "Selecciona un artículo de la tabla.")
            return
        title, date = self.selected
        if not messagebox.askyesno("Borrar", f"¿Seguro que quieres borrar el artículo {title} ({date})?"):
            return
        try:
            deleted = deleteArticle(title, date)
        except Exception as e:
            if not hasRelationsError(e):
                showError(e)
                return
            answer = messagebox.askyesno(
                "Tiene relaciones",
                "El artículo tiene autor, etiquetas, categorías o comentarios.\n"
                "¿Borrarlo de todos modos con sus relaciones?\n\n"
                "OJO: también se borran todos sus comentarios.",
            )
            if not answer:
                return
            try:
                deleted = deleteArticle(title, date, detach=True)
            except Exception as e:
                showError(e)
                return
        if not deleted:
            messagebox.showerror("No encontrado", "Ese artículo ya no existe.")
        self.refresh()

    # ---------- panel de detalle ----------

    def showDetail(self):
        self.commentsTable.delete(*self.commentsTable.get_children())
        self.detail = None
        if not self.selected:
            self.detailTitle.config(text="Selecciona un artículo")
            for label in (self.authorLabel, self.tagsLabel, self.categoriesLabel):
                label.config(text="-")
            return
        try:
            detail = getArticleDetail(*self.selected)
        except Exception as e:
            showError(e)
            return
        if detail is None:
            self.detailTitle.config(text="El artículo ya no existe")
            return
        self.detail = detail
        self.detailTitle.config(text=f"{detail['title']} ({detail['date']})")
        author = detail["author"]
        self.authorLabel.config(text=f"{author['name']} ({author['email']})" if author else "(sin autor)")
        self.tagsLabel.config(text=", ".join(detail["tags"]) or "(ninguna)")
        self.categoriesLabel.config(text=", ".join(detail["categories"]) or "(ninguna)")
        for c in detail["comments"]:
            self.commentsTable.insert("", "end", values=(c["name"], c["author"] or "(sin autor)"))

    def needArticle(self):
        if not self.selected:
            messagebox.showwarning("Detalle", "Primero selecciona un artículo de la tabla.")
            return False
        return True

    def assignAuthor(self):
        if not self.needArticle():
            return
        if not checkFields({"Autor": self.author.get()}):
            return
        try:
            ok = linkArticleAuthor(self.users[self.author.get()], *self.selected)
        except Exception as e:
            showError(e)
            return
        if not ok:
            messagebox.showerror("No encontrado", "El usuario o el artículo ya no existen. Presiona Refrescar.")
        self.showDetail()

    def changeLink(self, fn, value, field, notFound):
        # sirve para agregar o quitar etiquetas y categorías
        if not self.needArticle():
            return
        if not checkFields({field: value}):
            return
        try:
            ok = fn(value, *self.selected)
        except Exception as e:
            showError(e)
            return
        if not ok:
            messagebox.showwarning("Aviso", notFound)
        self.showDetail()

    def addTag(self):
        self.changeLink(addTagToArticle, self.tag.get(), "Etiqueta", "La etiqueta o el artículo ya no existen.")

    def removeTag(self):
        self.changeLink(removeTagFromArticle, self.tag.get(), "Etiqueta", "El artículo no tiene esa etiqueta.")

    def addCategory(self):
        self.changeLink(
            addCategoryToArticle, self.category.get(), "Categoría", "La categoría o el artículo ya no existen."
        )

    def removeCategory(self):
        self.changeLink(
            removeCategoryFromArticle, self.category.get(), "Categoría", "El artículo no está en esa categoría."
        )

    # ---------- ventana para agregar comentario ----------

    def openCommentDialog(self):
        if not self.needArticle():
            return
        dialog = tk.Toplevel(self)
        dialog.title("Agregar comentario")
        dialog.transient(self.winfo_toplevel())
        dialog.resizable(False, False)
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"Artículo: {self.selected[0]} ({self.selected[1]})").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )
        ttk.Label(frame, text="Comentario:").grid(row=1, column=0, sticky="w")
        name = tk.StringVar()
        ttk.Entry(frame, textvariable=name, width=40).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(frame, text="URL:").grid(row=2, column=0, sticky="w")
        url = tk.StringVar()
        ttk.Entry(frame, textvariable=url, width=40).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(frame, text="Autor:").grid(row=3, column=0, sticky="w")
        author = tk.StringVar()
        ttk.Combobox(frame, textvariable=author, values=list(self.users), state="readonly", width=38).grid(
            row=3, column=1, padx=5, pady=2
        )

        def save():
            fields = {"Comentario": name.get().strip(), "URL": url.get().strip(), "Autor": author.get()}
            if not checkFields(fields):
                return
            try:
                comment = addComment(
                    self.users[author.get()], *self.selected, fields["Comentario"], fields["URL"]
                )
            except Exception as e:
                showError(e, duplicate=f"Ya existe un comentario con la URL {fields['URL']}.")
                return
            if comment is None:
                messagebox.showerror("No encontrado", "El autor o el artículo ya no existen.")
            dialog.destroy()
            self.showDetail()

        buttons = ttk.Frame(frame)
        buttons.grid(row=4, column=0, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Button(buttons, text="Guardar", command=save).pack(side="left", padx=2)
        ttk.Button(buttons, text="Cancelar", command=dialog.destroy).pack(side="left", padx=2)
        dialog.grab_set()
        return dialog
