from tkinter import ttk, messagebox
import tkinter as tk

from animatedBackground import AnimatedBackground
from database import Database
from utils import hash_sha256
from placeholderEntry import PlaceholderEntry
from styleManager import StyleManager




class AdminScene(ttk.Frame):
    """Lightweight rewrite of AdminMainScene – focuses on CRUD actions."""

    def __init__(self, master, db: Database, user_id: int, sm: StyleManager):
        super().__init__(master)
        self.db, self.user_id, self.sm = db, user_id, sm
        master.title("PyGrader – Admin")
        master.geometry("1180x680")
        self.grid(sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        AnimatedBackground(self)

        sidebar = ttk.Frame(self, width=260)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        sidebar.rowconfigure(0, weight=1)

        ttk.Label(sidebar, text="Admin", style="Header.TLabel")\
            .grid(row=0, column=0, pady=(20, 10), padx=30)

        # corrected: _add_user instead of _submit_user
        ttk.Button(
            sidebar,
            text="Add User",
            style="Accent.TButton",
            command=self._add_user
        ).grid(row=1, column=0, sticky="ew", padx=30, pady=2)

        ttk.Button(
            sidebar,
            text="Add Task",
            style="Accent.TButton",
            command=self._add_task
        ).grid(row=2, column=0, sticky="ew", padx=30, pady=2)

        ttk.Button(
            sidebar,
            text="Users",
            style="Accent.TButton",
            command=self._list_users
        ).grid(row=3, column=0, sticky="ew", padx=30, pady=2)

        ttk.Button(
            sidebar,
            text="Toggle Theme",
            command=self.sm.toggle_theme
        ).grid(row=4, column=0, sticky="ew", padx=30, pady=(20, 0))

        self.content = ttk.Frame(self)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._show_welcome()

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_welcome(self):
        self._clear()
        ttk.Label(self.content, text="Welcome, admin!", style="Header.TLabel").pack(pady=40)

    def _submit_user(self, name: str, password: str, is_admin: bool):
        if not (name and password):
            messagebox.showwarning("Missing", "Both fields required")
            return
        self.db.add_user(name, hash_sha256(password), is_admin)

        # --- NEW: print entire User table ---
        print("\n=== User table ===")
        for uid, uname, hpwd, adm in self.db.get_users():
            print(f"{uid}\t{uname}\t{hpwd}\t{adm}")
        print("==================\n")
        # -------------------------------------

        messagebox.showinfo("Success", f"Created user '{name}'.")
        self._show_welcome()

    def _submit_task(self, entries):
        title = entries["Title"].value()
        desc = entries["Description"].value()
        exp = entries["Expiration (YYYY-MM-DD)"].value() or None
        rules = entries["Validation Rules"].value()
        if not (title and desc and rules):
            messagebox.showwarning("Missing", "Title, description and rules required.")
            return
        self.db.add_task(title, desc, exp, rules)

        # --- NEW: print entire Task table ---
        print("\n=== Task table ===")
        for tid, ttitle, tdesc, texp, trules in self.db.get_tasks():
            print(f"{tid}\t{ttitle}\t{tdesc}\t{texp}\t{trules}")
        print("==================\n")
        # -------------------------------------

        messagebox.showinfo("Success", "Task added.")
        self._show_welcome()

    def _add_task(self):
        self._clear()
        ttk.Label(self.content, text="Add Task", style="Header.TLabel").pack(pady=20)
        entries = {}
        for label in ("Title", "Description", "Expiration (YYYY-MM-DD)", "Validation Rules"):
            e = PlaceholderEntry(self.content, label)
            e.pack(fill="x", padx=200, pady=5)
            entries[label] = e
        ttk.Button(
            self.content,
            text="Create",
            style="Accent.TButton",
            command=lambda: self._submit_task(entries),
        ).pack(pady=20)



    def _list_users(self):
        self._clear()
        ttk.Label(self.content, text="All Users", style="Header.TLabel").pack(pady=20)
        tree = ttk.Treeview(self.content, columns=("ID", "Name", "Admin"), show="headings", height=15)
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Name")
        tree.heading("Admin", text="Admin")
        tree.pack(fill="both", expand=True, padx=40, pady=10)
        for uid, name, _, adm in self.db.get_users():
            tree.insert("", tk.END, values=(uid, name, "✅" if adm else ""))

    def _add_user(self):
                """Show the Add User form."""
                self._clear()
                ttk.Label(self.content, text = "Add User", style = "Header.TLabel") \
                    .pack(pady = 20)

                # username & password entries
                name = PlaceholderEntry(self.content, "Username")
                pwd = PlaceholderEntry(self.content, "Password", show = "*")
                is_admin = tk.BooleanVar()

                name.pack(fill = "x", padx = 200, pady = 5)
                pwd.pack(fill = "x", padx = 200, pady = 5)
                ttk.Checkbutton(self.content, text = "Admin", variable = is_admin) \
                    .pack(pady = 10)

                ttk.Button(
                        self.content,
                        text = "Create",
                        style = "Accent.TButton",
                        command = lambda: self._submit_user(
                                name.value(), pwd.value(), is_admin.get()
                        ),
                ).pack(pady = 20)