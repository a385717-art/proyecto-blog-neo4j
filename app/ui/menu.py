"""Ventana principal con una pestaña por entidad."""

from tkinter import ttk

from crud import (
    createCategory,
    createTag,
    deleteCategory,
    deleteTag,
    getCategories,
    getTags,
    updateCategory,
    updateTag,
)
from ui.articles_tab import ArticlesTab
from ui.comments_tab import CommentsTab
from ui.name_url_tab import NameUrlTab
from ui.users_tab import UsersTab


class MainWindow:
    def __init__(self, root):
        root.title("Blog Neo4j")
        root.geometry("1150x650")
        root.minsize(900, 550)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.add(UsersTab(self.notebook), text="Usuarios")
        self.notebook.add(ArticlesTab(self.notebook), text="Artículos")
        categories = NameUrlTab(
            self.notebook, "categoría", getCategories, createCategory, updateCategory, deleteCategory
        )
        self.notebook.add(categories, text="Categorías")
        # en las etiquetas la URL es opcional
        tags = NameUrlTab(self.notebook, "etiqueta", getTags, createTag, updateTag, deleteTag, urlRequired=False)
        self.notebook.add(tags, text="Etiquetas")
        self.notebook.add(CommentsTab(self.notebook), text="Comentarios")

        self.notebook.bind("<<NotebookTabChanged>>", self.onTabChanged)

    def onTabChanged(self, event):
        # al cambiar de pestaña se recargan los combobox por si hay usuarios,
        # artículos, etiquetas o categorías nuevas
        tab = self.notebook.nametowidget(self.notebook.select())
        if hasattr(tab, "reloadOptions"):
            tab.reloadOptions()
