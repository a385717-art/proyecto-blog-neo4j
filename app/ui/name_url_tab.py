"""Pestaña para entidades que solo tienen nombre y URL (categorías y etiquetas)."""

import tkinter as tk
from tkinter import messagebox, ttk

from ui.common import checkFields, hasRelationsError, showError


class NameUrlTab(ttk.Frame):
    # entity es el nombre en singular ("categoría" o "etiqueta")
    # urlRequired dice si la URL es obligatoria
    def __init__(self, parent, entity, getAll, create, update, delete, urlRequired=True):
        super().__init__(parent, padding=10)
        self.entity = entity
        self.getAll = getAll
        self.createFn = create
        self.updateFn = update
        self.deleteFn = delete
        self.urlRequired = urlRequired
        self.selected = None  # nombre del registro seleccionado

        # tabla
        self.table = ttk.Treeview(self, columns=("name", "url"), show="headings", height=15)
        self.table.heading("name", text="Nombre")
        self.table.heading("url", text="URL")
        self.table.column("name", width=220)
        self.table.column("url", width=380)
        self.table.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")
        self.table.bind("<<TreeviewSelect>>", self.onSelect)

        # campos de captura
        form = ttk.Frame(self)
        form.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w")
        self.name = tk.StringVar()
        self.nameEntry = ttk.Entry(form, textvariable=self.name, width=40)
        self.nameEntry.grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(form, text="(el nombre no se puede cambiar)").grid(row=0, column=2, sticky="w")
        ttk.Label(form, text="URL:").grid(row=1, column=0, sticky="w")
        self.url = tk.StringVar()
        ttk.Entry(form, textvariable=self.url, width=60).grid(row=1, column=1, columnspan=2, sticky="w", padx=5)
        if not urlRequired:
            ttk.Label(form, text="(opcional)").grid(row=1, column=3, sticky="w")

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

    def refresh(self):
        self.table.delete(*self.table.get_children())
        try:
            rows = self.getAll()
        except Exception as e:
            showError(e)
            return
        for row in rows:
            self.table.insert("", "end", values=(row["name"], row["url"] or ""))
        self.clear()

    def clear(self):
        self.selected = None
        self.table.selection_remove(self.table.selection())
        self.name.set("")
        self.url.set("")
        self.nameEntry.state(["!disabled"])

    def onSelect(self, event):
        items = self.table.selection()
        if not items:
            return
        name, url = self.table.item(items[0], "values")
        self.selected = name
        self.name.set(name)
        self.url.set(url)
        # el nombre es el identificador, por eso se bloquea al editar
        self.nameEntry.state(["disabled"])

    def readFields(self):
        # regresa (nombre, url) o None si falta algo
        name = self.name.get().strip()
        url = self.url.get().strip()
        fields = {"Nombre": name}
        if self.urlRequired:
            fields["URL"] = url
        if not checkFields(fields):
            return None
        return name, url or None

    def create(self):
        if self.selected:
            messagebox.showinfo("Crear", f"Primero presiona Limpiar para capturar una {self.entity} nueva.")
            return
        values = self.readFields()
        if values is None:
            return
        name, url = values
        try:
            self.createFn(name, url)
        except Exception as e:
            showError(e, duplicate=f"Ya existe una {self.entity} con el nombre {name}.")
            return
        self.refresh()

    def update(self):
        if not self.selected:
            messagebox.showwarning("Actualizar", f"Selecciona una {self.entity} de la tabla.")
            return
        values = self.readFields()
        if values is None:
            return
        try:
            # el nombre no cambia, solo la URL
            row = self.updateFn(self.selected, self.selected, values[1])
        except Exception as e:
            showError(e)
            return
        if row is None:
            messagebox.showerror("No encontrado", f"Esa {self.entity} ya no existe. Presiona Refrescar.")
        self.refresh()

    def delete(self):
        if not self.selected:
            messagebox.showwarning("Borrar", f"Selecciona una {self.entity} de la tabla.")
            return
        name = self.selected
        if not messagebox.askyesno("Borrar", f"¿Seguro que quieres borrar la {self.entity} {name}?"):
            return
        try:
            deleted = self.deleteFn(name)
        except Exception as e:
            if not hasRelationsError(e):
                showError(e)
                return
            answer = messagebox.askyesno(
                "Tiene relaciones",
                f"La {self.entity} está asignada a uno o más artículos.\n"
                "¿Borrarla de todos modos con sus relaciones?\n\n"
                f"Los artículos no se borran, solo se quedan sin esta {self.entity}.",
            )
            if not answer:
                return
            try:
                deleted = self.deleteFn(name, detach=True)
            except Exception as e:
                showError(e)
                return
        if not deleted:
            messagebox.showerror("No encontrado", f"Esa {self.entity} ya no existe.")
        self.refresh()
