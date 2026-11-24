"""Pestaña de usuarios."""

import tkinter as tk
from tkinter import messagebox, ttk

from crud import createUser, deleteUser, getUsers, updateUser
from ui.common import checkFields, hasRelationsError, showError


class UsersTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.selected = None  # correo del usuario seleccionado

        # tabla
        self.table = ttk.Treeview(self, columns=("name", "email"), show="headings", height=15)
        self.table.heading("name", text="Nombre")
        self.table.heading("email", text="Correo")
        self.table.column("name", width=220)
        self.table.column("email", width=280)
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
        ttk.Entry(form, textvariable=self.name, width=40).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(form, text="Correo:").grid(row=1, column=0, sticky="w")
        self.email = tk.StringVar()
        self.emailEntry = ttk.Entry(form, textvariable=self.email, width=40)
        self.emailEntry.grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(form, text="(el correo no se puede cambiar)").grid(row=1, column=2, sticky="w")

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
            users = getUsers()
        except Exception as e:
            showError(e)
            return
        for user in sorted(users, key=lambda u: (u["name"] or "").lower()):
            self.table.insert("", "end", values=(user["name"], user["email"]))
        self.clear()

    def clear(self):
        self.selected = None
        self.table.selection_remove(self.table.selection())
        self.name.set("")
        self.email.set("")
        self.emailEntry.state(["!disabled"])

    def onSelect(self, event):
        items = self.table.selection()
        if not items:
            return
        name, email = self.table.item(items[0], "values")
        self.selected = email
        self.name.set(name)
        self.email.set(email)
        # el correo es el identificador, por eso se bloquea al editar
        self.emailEntry.state(["disabled"])

    def create(self):
        name = self.name.get().strip()
        email = self.email.get().strip()
        if self.selected:
            messagebox.showinfo("Crear", "Primero presiona Limpiar para capturar un usuario nuevo.")
            return
        if not checkFields({"Nombre": name, "Correo": email}):
            return
        try:
            createUser(name, email)
        except Exception as e:
            showError(e, duplicate=f"Ya existe un usuario con el correo {email}.")
            return
        self.refresh()

    def update(self):
        if not self.selected:
            messagebox.showwarning("Actualizar", "Selecciona un usuario de la tabla.")
            return
        name = self.name.get().strip()
        if not checkFields({"Nombre": name}):
            return
        try:
            user = updateUser(self.selected, name)
        except Exception as e:
            showError(e)
            return
        if user is None:
            messagebox.showerror("No encontrado", "Ese usuario ya no existe. Presiona Refrescar.")
        self.refresh()

    def delete(self):
        if not self.selected:
            messagebox.showwarning("Borrar", "Selecciona un usuario de la tabla.")
            return
        email = self.selected
        if not messagebox.askyesno("Borrar", f"¿Seguro que quieres borrar al usuario {email}?"):
            return
        try:
            deleted = deleteUser(email)
        except Exception as e:
            if not hasRelationsError(e):
                showError(e)
                return
            # tiene artículos o comentarios ligados
            answer = messagebox.askyesno(
                "Tiene relaciones",
                "El usuario tiene artículos o comentarios.\n"
                "¿Borrarlo de todos modos con sus relaciones?\n\n"
                "Sus artículos y comentarios no se borran, se quedan sin autor.",
            )
            if not answer:
                return
            try:
                deleted = deleteUser(email, detach=True)
            except Exception as e:
                showError(e)
                return
        if not deleted:
            messagebox.showerror("No encontrado", "Ese usuario ya no existe.")
        self.refresh()
