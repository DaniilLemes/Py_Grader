import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database import Database
from styleManager import StyleManager
from utils import hash_sha256
from placeholderEntry import PlaceholderEntry
import random

class AdminScene(ctk.CTkFrame):
    """Redesigned AdminScene with LoginScene's aesthetic – sleek, modern, with animated particles."""

    def __init__(self, master, db: Database, user_id: int, sm: StyleManager):
        super().__init__(master, fg_color="transparent")
        self.db, self.user_id, self.sm = db, user_id, sm
        self.master.configure(bg='#000000')
        self.master.geometry("1180x680")
        self.master.resizable(False, False)
        self.master.title("PyGrader – Admin")

        # Canvas for animated particle background
        self.canvas = tk.Canvas(self, bg='#000000', highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.grid(sticky="nsew")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        # Initialize particles
        self.particles = []
        self.num_particles = 50
        self._init_particles()

        # Build UI
        self._build()

        # Start particle animation
        self._animate_particles()

    def _init_particles(self):
        """Initialize particles for atmospheric background"""
        for _ in range(self.num_particles):
            x = random.randint(0, 1180)
            y = random.randint(0, 680)
            size = random.uniform(1, 2.5)
            speed_x = random.uniform(-0.5, 0.5)
            speed_y = random.uniform(-0.5, 0.5)
            color = random.choice(['#f09c3a', '#ffffff', '#666666'])
            particle = self.canvas.create_oval(x, y, x + size, y + size,
                                               fill=color, outline='', stipple="gray50")
            self.particles.append({
                'id': particle,
                'x': x, 'y': y,
                'speed_x': speed_x,
                'speed_y': speed_y,
                'size': size
            })

    def _animate_particles(self):
        """Smooth particle animation"""
        for particle in self.particles:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']

            # Bounce off edges with slight randomness
            if particle['x'] < 0 or particle['x'] > 1180:
                particle['speed_x'] = -particle['speed_x'] * random.uniform(0.8, 1.2)
            if particle['y'] < 0 or particle['y'] > 680:
                particle['speed_y'] = -particle['speed_y'] * random.uniform(0.8, 1.2)

            self.canvas.coords(particle['id'],
                               particle['x'], particle['y'],
                               particle['x'] + particle['size'],
                               particle['y'] + particle['size'])
        self.master.after(30, self._animate_particles)

    def _build(self):
        """Build UI with LoginScene's aesthetic"""
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=260, fg_color="#1a1a1a", corner_radius=12, border_width=1, border_color="#f09c3a")
        sidebar.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)
        sidebar.grid_propagate(False)

        # Sidebar header
        header_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20, 10), padx=15)

        # Logo: "PyGrader"
        logo_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_container.pack(anchor="center")

        ctk.CTkLabel(
            logo_container,
            text="Py",
            font=("Helvetica", 28, "bold"),
            text_color="#ffffff"
        ).pack(side="left")

        grader_frame = ctk.CTkFrame(
            logo_container,
            fg_color="#f09c3a",
            corner_radius=8,
            width=100, height=35
        )
        grader_frame.pack(side="left", padx=(3, 0))

        ctk.CTkLabel(
            grader_frame,
            text="Grader",
            font=("Helvetica", 28, "bold"),
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Sidebar buttons
        buttons = [
            ("🚀 Add User", self._add_user),
            ("📝 Add Task", self._add_task),
            ("👥 Users", self._list_users),
            ("🌗 Toggle Theme", self.sm.toggle_theme)
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                font=("Helvetica", 13, "bold"),
                height=40,
                fg_color="#f09c3a",
                hover_color="#ff8800",
                text_color="#000000",
                corner_radius=10
            )
            btn.pack(fill="x", padx=20, pady=5)
            btn.bind("<Button-1>", self._animate_button)

        # Content area
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._show_welcome()

    def _animate_button(self, event):
        """Button click animation"""
        try:
            btn = event.widget
            btn.configure(fg_color="#ff6600")
            self.master.after(150, lambda: btn.configure(fg_color="#f09c3a"))
        except:
            pass

    def _clear(self):
        """Clear content area"""
        for w in self.content.winfo_children():
            w.destroy()

    def _show_welcome(self):
        """Display welcome message"""
        self._clear()
        ctk.CTkLabel(
            self.content,
            text="Welcome, admin! 😎",
            font=("Helvetica", 28, "bold"),
            text_color="#ffffff"
        ).pack(pady=40)
        ctk.CTkLabel(
            self.content,
            text="My Step-Function Is Stuck In A Loop 👄, or its so empty here?",
            font=("Helvetica", 16, "italic"),
            text_color="#f09c3a"
        ).pack(pady=10)

    def _submit_user(self, name: str, password: str, is_admin: bool):
        """Handle user creation"""
        if not (name and password):
            messagebox.showwarning("Missing", "Both fields required 💔")
            return
        self.db.add_user(name, hash_sha256(password), is_admin)

        print("\n=== User table ===")
        for uid, uname, hpwd, adm in self.db.get_users():
            print(f"{uid}\t{uname}\t{hpwd}\t{adm}")
        print("==================\n")

        messagebox.showinfo("Success", f"Created user '{name}'! 🎉")
        self._show_welcome()

    def _submit_task(self, entries):
        """Handle task creation"""
        title = entries["Title"].value()
        desc = entries["Description"].value()
        exp = entries["Expiration (YYYY-MM-DD)"].value() or None
        rules = entries["Validation Rules"].value()
        if not (title and desc and rules):
            messagebox.showwarning("Missing", "Title, description, and rules required 💔")
            return
        self.db.add_task(title, desc, exp, rules)

        print("\n=== Task table ===")
        for tid, ttitle, tdesc, texp, trules in self.db.get_tasks():
            print(f"{tid}\t{ttitle}\t{tdesc}\t{texp}\t{trules}")
        print("==================\n")

        messagebox.showinfo("Success", "Task added! 🚀")
        self._show_welcome()

    def _add_task(self):
        """Show the Add Task form"""
        self._clear()
        ctk.CTkLabel(
            self.content,
            text="Add Task 📝",
            font=("Helvetica", 24, "bold"),
            text_color="#ffffff"
        ).pack(pady=20)

        entries = {}
        for label in ("Title", "Description", "Expiration (YYYY-MM-DD)", "Validation Rules"):
            e = ctk.CTkEntry(
                self.content,
                placeholder_text=f"✍️ {label}",
                font=("Helvetica", 12),
                height=35,
                fg_color="#242424",
                text_color="#ffffff",
                placeholder_text_color="#999999",
                border_color="#f09c3a",
                border_width=1,
                corner_radius=8
            )
            e.pack(fill="x", padx=200, pady=5)
            entries[label] = e

        ctk.CTkButton(
            self.content,
            text="Create 🚀",
            command=lambda: self._submit_task(entries),
            font=("Helvetica", 13, "bold"),
            height=40,
            fg_color="#f09c3a",
            hover_color="#ff8800",
            text_color="#000000",
            corner_radius=10
        ).pack(pady=20)

    def _list_users(self):
        """Display list of users"""
        self._clear()
        ctk.CTkLabel(
            self.content,
            text="All Users 👥",
            font=("Helvetica", 24, "bold"),
            text_color="#ffffff"
        ).pack(pady=20)

        # Create a canvas with scrollbar
        canvas = tk.Canvas(self.content, bg='#000000', highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(self.content, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="transparent")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=40, pady=10)
        scrollbar.pack(side="right", fill="y")

        # User list
        headers = ["ID", "Name", "Admin"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                scrollable_frame,
                text=header,
                font=("Helvetica", 14, "bold"),
                text_color="#f09c3a"
            ).grid(row=0, column=col, padx=20, pady=5, sticky="w")

        for row, (uid, name, _, adm) in enumerate(self.db.get_users(), 1):
            ctk.CTkLabel(
                scrollable_frame,
                text=str(uid),
                font=("Helvetica", 12),
                text_color="#ffffff"
            ).grid(row=row, column=0, padx=20, pady=5, sticky="w")
            ctk.CTkLabel(
                scrollable_frame,
                text=name,
                font=("Helvetica", 12),
                text_color="#ffffff"
            ).grid(row=row, column=1, padx=20, pady=5, sticky="w")
            ctk.CTkLabel(
                scrollable_frame,
                text="✅" if adm else "",
                font=("Helvetica", 12),
                text_color="#f09c3a"
            ).grid(row=row, column=2, padx=20, pady=5, sticky="w")

    def _add_user(self):
        """Show the Add User form"""
        self._clear()
        ctk.CTkLabel(
            self.content,
            text="Add User 🚀",
            font=("Helvetica", 24, "bold"),
            text_color="#ffffff"
        ).pack(pady=20)

        name = ctk.CTkEntry(
            self.content,
            placeholder_text="👤 Username",
            font=("Helvetica", 12),
            height=35,
            fg_color="#242424",
            text_color="#ffffff",
            placeholder_text_color="#999999",
            border_color="#f09c3a",
            border_width=1,
            corner_radius=8
        )
        name.pack(fill="x", padx=200, pady=5)

        pwd = ctk.CTkEntry(
            self.content,
            placeholder_text="🔐 Password",
            show="●",
            font=("Helvetica", 12),
            height=35,
            fg_color="#242424",
            text_color="#ffffff",
            placeholder_text_color="#999999",
            border_color="#f09c3a",
            border_width=1,
            corner_radius=8
        )
        pwd.pack(fill="x", padx=200, pady=5)

        is_admin = ctk.BooleanVar()
        admin_container = ctk.CTkFrame(self.content, fg_color="transparent")
        admin_container.pack(fill="x", pady=10, padx=200)

        ctk.CTkLabel(
            admin_container,
            text="🔥",
            font=("Arial", 14),
            text_color="#f09c3a"
        ).pack(side="left", padx=(5, 0))

        ctk.CTkCheckBox(
            admin_container,
            text="Admin Mode",
            variable=is_admin,
            font=("Helvetica", 11, "bold"),
            text_color="#ffffff",
            fg_color="#f09c3a",
            hover_color="#ff8800",
            corner_radius=6,
            border_width=1,
            border_color="#333333",
            checkbox_width=18,
            checkbox_height=18
        ).pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            self.content,
            text="Create 🚀",
            command=lambda: self._submit_user(name.get(), pwd.get(), is_admin.get()),
            font=("Helvetica", 13, "bold"),
            height=40,
            fg_color="#f09c3a",
            hover_color="#ff8800",
            text_color="#000000",
            corner_radius=10
        ).pack(pady=20)
