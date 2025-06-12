import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database import Database
from styleManager import StyleManager
from taskWindow import TaskWindow
import random
import datetime

class UserScene(ctk.CTkFrame):
    """User Interface with LoginScene's aesthetic – dark theme with animated particles and orange accents"""

    def __init__(self, master, db: Database, user_id: int, sm: StyleManager):
        super().__init__(master, fg_color="transparent")
        self.db, self.user_id, self.sm = db, user_id, sm
        self.master.configure(bg='#000000')
        self.master.geometry("1180x680")
        self.master.resizable(False, False)
        self.master.title("PyGrader – User")

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

    def _get_username(self):
        """Get username for current user"""
        for uid, name, _, _ in self.db.get_users():
            if uid == self.user_id:
                return name
        return "Unknown User"

    def _build(self):
        """Build UI with LoginScene's aesthetic"""
        # Sidebar
        sidebar = ctk.CTkFrame(
            self, width=260,
            fg_color="#1a1a1a",
            corner_radius=12,
            border_width=1,
            border_color="#f09c3a"
        )
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

        # Get username for welcome message
        username = self._get_username()
        welcome_label = ctk.CTkLabel(
            sidebar,
            text=f"👤 {username}",
            font=("Helvetica", 14, "bold"),
            text_color="#f09c3a"
        )
        welcome_label.pack(pady=15)

        # Sidebar buttons
        buttons = [
            ("📝 My Tasks", self._show_my_tasks),
            ("📊 All Tasks", self._show_all_tasks),
            ("👥 Users", self._show_users),
            ("🚪 Logout", self._logout)
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                font=("Helvetica", 13, "bold"),
                height=40,
                fg_color="#f09c3a" if text != "🚪 Logout" else "#e74c3c",
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

        # Show my tasks by default
        self._show_my_tasks()

    def _animate_button(self, event):
        """Button click animation"""
        try:
            btn = event.widget
            original_color = btn.cget("fg_color")
            hover_color = "#ff6600" if original_color == "#f09c3a" else "#c0392b"
            btn.configure(fg_color=hover_color)
            self.master.after(150, lambda: btn.configure(fg_color=original_color))
        except:
            pass

    def _clear(self):
        """Clear content area"""
        for w in self.content.winfo_children():
            w.destroy()

    def _logout(self):
        """Logout and return to login screen"""
        self.master.destroy()
        self.master.master.deiconify()

    def _open_task_window(self, task):
        """Open window to solve the selected task."""
        task_id, title, description, expiration, rules = task
        tests = list(self.db.get_test_cases(task_id))
        TaskWindow(self.master, title, description, expiration, tests, self.sm)
    def _show_my_tasks(self):
        """Display tasks assigned to the current user"""
        self._clear()

        # Header
        ctk.CTkLabel(
            self.content,
            text="📝 My Assigned Tasks",
            font=("Helvetica", 24, "bold"),
            text_color="#ffffff"
        ).pack(pady=(10, 20))

        # Get tasks from database
        tasks = list(self.db.get_tasks_for_user(self.user_id))

        if not tasks:
            ctk.CTkLabel(
                self.content,
                text="No tasks assigned to you yet. Contact admin! 📞",
                font=("Helvetica", 16, "italic"),
                text_color="#f09c3a"
            ).pack(pady=50)
            return

        # Create scrollable frame for tasks
        container = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent",
            height=500
        )
        container.pack(fill="both", expand=True, padx=20, pady=10)

        for task in tasks:
            task_id, title, description, expiration, rules = task

            # Task card
            card = ctk.CTkFrame(
                container,
                fg_color="#1a1a1a",
                corner_radius=12,
                border_width=1,
                border_color="#f09c3a"
            )
            card.pack(fill="x", pady=10, padx=5)

            # Task header
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(15, 5))

            ctk.CTkLabel(
                header_frame,
                text=title,
                font=("Helvetica", 18, "bold"),
                text_color="#f09c3a"
            ).pack(side="left")

            # Expiration info
            exp_info = f"⏱️ Due: {expiration}" if expiration else "⏱️ No deadline"
            exp_label = ctk.CTkLabel(
                header_frame,
                text=exp_info,
                font=("Helvetica", 12),
                text_color="#aaaaaa"
            )
            exp_label.pack(side="right", padx=10)

            # Task description
            desc_frame = ctk.CTkFrame(card, fg_color="transparent")
            desc_frame.pack(fill="x", padx=15, pady=(0, 10))

            ctk.CTkLabel(
                desc_frame,
                text=description,
                font=("Helvetica", 13),
                text_color="#ffffff",
                wraplength=700,
                justify="left"
            ).pack(anchor="w")

            # Validation rules
            if rules:
                rules_frame = ctk.CTkFrame(card, fg_color="transparent")
                rules_frame.pack(fill="x", padx=15, pady=(0, 10))

                ctk.CTkLabel(
                    rules_frame,
                    text="📋 Rules:",
                    font=("Helvetica", 12, "bold"),
                    text_color="#f09c3a"
                ).pack(anchor="w")


                ctk.CTkLabel(
                    rules_frame,
                    text=rules,
                    font=("Helvetica", 11),
                    text_color="#cccccc",
                    wraplength=700,
                    justify="left"
                ).pack(anchor="w", padx=(20, 0))



            ctk.CTkButton(
                card,
                text="Solve",
                command=lambda t=task: self._open_task_window(t),
                font=("Helvetica", 12, "bold"),
                fg_color="#f09c3a",
                hover_color="#ff8800",
                text_color="#000000",
                corner_radius=8,
            ).pack(pady=(0, 10))

    def _show_all_tasks(self):
        """Display all tasks in the system"""
        self._clear()

        # Header
        ctk.CTkLabel(
            self.content,
            text="📊 All Tasks in System",
            font=("Helvetica", 24, "bold"),
            text_color="#ffffff"
        ).pack(pady=(10, 20))

        # Get all tasks from database
        tasks = list(self.db.get_tasks())

        if not tasks:
            ctk.CTkLabel(
                self.content,
                text="No tasks in the system yet. Admin needs to create some! 🛠️",
                font=("Helvetica", 16, "italic"),
                text_color="#f09c3a"
            ).pack(pady=50)
            return

        # Create scrollable frame for tasks
        container = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent",
            height=500
        )
        container.pack(fill="both", expand=True, padx=20, pady=10)

        for task in tasks:
            task_id, title, description, expiration, rules = task

            # Task card
            card = ctk.CTkFrame(
                container,
                fg_color="#1a1a1a",
                corner_radius=12,
                border_width=1,
                border_color="#f09c3a"
            )
            card.pack(fill="x", pady=10, padx=5)

            # Task header
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(15, 5))

            ctk.CTkLabel(
                header_frame,
                text=f"#{task_id}: {title}",
                font=("Helvetica", 18, "bold"),
                text_color="#f09c3a"
            ).pack(side="left")

            # Expiration info
            exp_info = f"⏱️ Due: {expiration}" if expiration else "⏱️ No deadline"
            exp_label = ctk.CTkLabel(
                header_frame,
                text=exp_info,
                font=("Helvetica", 12),
                text_color="#aaaaaa"
            )
            exp_label.pack(side="right", padx=10)

            # Task description
            desc_frame = ctk.CTkFrame(card, fg_color="transparent")
            desc_frame.pack(fill="x", padx=15, pady=(0, 10))

            ctk.CTkLabel(
                desc_frame,
                text=description,
                font=("Helvetica", 13),
                text_color="#ffffff",
                wraplength=700,
                justify="left"
            ).pack(anchor="w")

            # Validation rules
            if rules:
                rules_frame = ctk.CTkFrame(card, fg_color="transparent")
                rules_frame.pack(fill="x", padx=15, pady=(0, 15))

                ctk.CTkLabel(
                    rules_frame,
                    text="📋 Validation Rules:",
                    font=("Helvetica", 12, "bold"),
                    text_color="#f09c3a"
                ).pack(anchor="w")

                ctk.CTkLabel(
                    rules_frame,
                    text=rules,
                    font=("Helvetica", 11),
                    text_color="#cccccc",
                    wraplength=700,
                    justify="left"
                ).pack(anchor="w", padx=(20, 0))

            ctk.CTkButton(
                card,
                text="Solve",
                command=lambda t=task: self._open_task_window(t),
                font=("Helvetica", 12, "bold"),
                fg_color="#f09c3a",
                hover_color="#ff8800",
                text_color="#000000",
                corner_radius=8,
            ).pack(pady=(0, 10))

    def _show_users(self):
        """Display all users in the system"""
        self._clear()

        # Header
        ctk.CTkLabel(
            self.content,
            text="👥 System Users",
            font=("Helvetica", 24, "bold"),
            text_color="#ffffff"
        ).pack(pady=(10, 20))

        # Get users from database
        users = list(self.db.get_users())

        if not users:
            ctk.CTkLabel(
                self.content,
                text="No users in the system! 🤔",
                font=("Helvetica", 16, "italic"),
                text_color="#f09c3a"
            ).pack(pady=50)
            return

        # Create table frame
        table_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Table headers
        headers = ["ID", "Username", "Role", "Status"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                table_frame,
                text=header,
                font=("Helvetica", 14, "bold"),
                text_color="#f09c3a",
                width=100 if col == 0 else 200,
                anchor="center" if col == 0 else "w"
            ).grid(row=0, column=col, padx=5, pady=5, sticky="ew")

        # Table rows
        for row, user in enumerate(users, 1):
            user_id, username, hashed_password, is_admin = user

            # User ID
            ctk.CTkLabel(
                table_frame,
                text=str(user_id),
                font=("Helvetica", 12),
                text_color="#ffffff",
                width=100,
                anchor="center"
            ).grid(row=row, column=0, padx=5, pady=5)

            # Username (highlight current user)
            user_color = "#f09c3a" if user_id == self.user_id else "#ffffff"
            current_marker = " (You)" if user_id == self.user_id else ""

            ctk.CTkLabel(
                table_frame,
                text=username + current_marker,
                font=("Helvetica", 12, "bold" if user_id == self.user_id else "normal"),
                text_color=user_color,
                width=200,
                anchor="w"
            ).grid(row=row, column=1, padx=5, pady=5, sticky="w")

            # Role
            role = "Admin" if is_admin else "User"
            role_color = "#e74c3c" if is_admin else "#2ecc71"

            ctk.CTkLabel(
                table_frame,
                text=role,
                font=("Helvetica", 12, "bold"),
                text_color=role_color,
                width=200,
                anchor="w"
            ).grid(row=row, column=2, padx=5, pady=5, sticky="w")

            # Status (active since they have password)
            status = "Active" if hashed_password else "Inactive"
            status_color = "#2ecc71" if hashed_password else "#e74c3c"

            ctk.CTkLabel(
                table_frame,
                text=status,
                font=("Helvetica", 12),
                text_color=status_color,
                width=200,
                anchor="w"
            ).grid(row=row, column=3, padx=5, pady=5, sticky="w")
