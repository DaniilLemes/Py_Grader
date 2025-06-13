import customtkinter as ctk
import tkinter as tk
from styleManager import StyleManager
import random
from database import Database

class TaskWindow(ctk.CTkToplevel):
    """Window used to solve a task with animated particle background."""

    def __init__(
            self,
            master: tk.Misc,
            title: str,
            description: str,
            expiration: str | None,
            tests: list[tuple[str, str]],
            style_mgr: StyleManager,
            *,
            db: Database | None = None,
            user_id: int | None = None,
            task_id: int | None = None,
    ):
        super().__init__(master)
        self.sm = style_mgr
        self.tests = tests
        self.db = db
        self.user_id = user_id
        self.task_id = task_id
        self.configure(fg_color="#000000")
        self.geometry("720x480")  # Reduced window size
        self.resizable(False, False)
        self.title(f"PyGrader – {title}")

        # Make window modal and center it
        self.transient(master)
        self.after(0, self.grab_set)  # defer grab until window is visible
        self._center_window()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        # Canvas for animated particle background
        self.canvas = tk.Canvas(self, bg='#000000', highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Initialize particles
        self.particles = []
        self.num_particles = 40  # Reduced for smaller window
        self._init_particles()

        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent", border_width=0)
        container.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Top header bar
        self._create_header(container, title)

        # Main content area
        self._create_content(container, title, description, expiration, tests)

        # Start particle animation
        self._animate_particles()

    def _center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _init_particles(self):
        """Initialize particles for atmospheric background with valid stipple patterns"""
        for _ in range(self.num_particles):
            x = random.randint(0, 720)  # Adjusted for new window width
            y = random.randint(0, 480)  # Adjusted for new window height
            size = random.uniform(1.2, 3.5)  # Slightly smaller particles
            speed_x = random.uniform(-0.3, 0.3)  # Smoother movement
            speed_y = random.uniform(-0.3, 0.3)
            color = random.choice(['#f09c3a', '#ffffff', '#666666'])
            opacity = random.choice(['gray12', 'gray25', 'gray50', 'gray75'])
            particle = self.canvas.create_oval(
                x, y, x + size, y + size,
                fill=color, outline='', stipple=opacity, tags="particle"
            )
            self.particles.append({
                'id': particle,
                'x': x, 'y': y,
                'speed_x': speed_x,
                'speed_y': speed_y,
                'size': size
            })

    def _animate_particles(self):
        """Smooth particle animation"""
        try:
            for particle in self.particles:
                particle['x'] += particle['speed_x']
                particle['y'] += particle['speed_y']

                # Bounce with subtle randomness, adjusted for new window size
                if particle['x'] < 0 or particle['x'] > 720:
                    particle['speed_x'] = -particle['speed_x'] * random.uniform(0.85, 1.15)
                if particle['y'] < 0 or particle['y'] > 480:
                    particle['speed_y'] = -particle['speed_y'] * random.uniform(0.85, 1.15)

                self.canvas.coords(
                    particle['id'],
                    particle['x'], particle['y'],
                    particle['x'] + particle['size'],
                    particle['y'] + particle['size']
                )

            if self.winfo_exists():
                self.after(25, self._animate_particles)
        except Exception as e:
            print(f"Animation error: {e}")

    def _create_header(self, parent, title):
        """Create modern header with logo and title"""
        header_frame = ctk.CTkFrame(
            parent,
            fg_color="#1e1e1e",
            corner_radius=10,  # Reduced for elegance
            border_width=1,
            border_color="#f09c3a",
            height=48  # Smaller header
        )
        header_frame.pack(fill="x", padx=12, pady=(12, 8))
        header_frame.pack_propagate(False)

        # Left side - Logo
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="y", padx=12)

        logo_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        logo_container.pack(anchor="center", expand=True)

        ctk.CTkLabel(
            logo_container,
            text="Py",
            font=("SF Pro Display", 24, "bold"),  # Smaller font
            text_color="#ffffff"
        ).pack(side="left")

        grader_frame = ctk.CTkFrame(
            logo_container,
            fg_color="#f09c3a",
            corner_radius=8,  # Reduced radius
            width=80, height=28  # Smaller logo
        )
        grader_frame.pack(side="left", padx=(6, 0))

        ctk.CTkLabel(
            grader_frame,
            text="Grader",
            font=("SF Pro Display", 20, "bold"),  # Smaller font
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Center - Task title
        center_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        center_frame.pack(side="left", fill="both", expand=True, padx=15)

        ctk.CTkLabel(
            center_frame,
            text=f"📝 {title}",
            font=("SF Pro Display", 18, "bold"),  # Smaller font
            text_color="#f09c3a"
        ).pack(anchor="center", expand=True)

        # Right side - Close button
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="y", padx=12)

        close_btn = ctk.CTkButton(
            right_frame,
            text="✕",
            command=self.destroy,
            font=("SF Pro Display", 14, "bold"),  # Smaller font
            width=28, height=28,  # Smaller button
            fg_color="#e74c3c",
            hover_color="#c0392b",
            text_color="#ffffff",
            corner_radius=6
        )
        close_btn.pack(anchor="center", expand=True)
        close_btn.bind("<Button-1>", self._animate_close_button)

    def _create_content(self, parent, title, description, expiration, tests):
        """Create main content area with task description and code editor"""
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Left panel - Task description
        left_panel = ctk.CTkFrame(
            content_frame,
            fg_color="#1e1e1e",
            corner_radius=10,
            border_width=1,
            border_color="#30363d",  # Subtle border
            width=280  # Reduced width
        )
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        self._create_description_panel(left_panel, description, expiration, tests)

        # Right panel - Code editor
        right_panel = ctk.CTkFrame(
            content_frame,
            fg_color="#1e1e1e",
            corner_radius=10,
            border_width=1,
            border_color="#30363d"
        )
        right_panel.pack(side="right", fill="both", expand=True)

        self._create_editor_panel(right_panel)

    def _create_description_panel(self, parent, description, expiration, tests):
        """Create task description panel"""
        desc_header = ctk.CTkFrame(parent, fg_color="transparent", height=40)  # Smaller header
        desc_header.pack(fill="x", padx=10, pady=(10, 0))
        desc_header.pack_propagate(False)

        ctk.CTkLabel(
            desc_header,
            text="📋 Task Details",
            font=("SF Pro Display", 16, "bold"),  # Smaller font
            text_color="#f09c3a"
        ).pack(anchor="w", pady=6)

        if expiration:
            exp_frame = ctk.CTkFrame(
                parent,
                fg_color="#2a2a2a",
                corner_radius=8,  # Reduced radius
                border_width=1,
                border_color="#444444"
            )
            exp_frame.pack(fill="x", padx=10, pady=(0, 10))

            ctk.CTkLabel(
                exp_frame,
                text=f"⏱️ Deadline: {expiration}",
                font=("SF Pro Display", 12, "normal"),  # Smaller font
                text_color="#d3d3d3"
            ).pack(pady=6)

        desc_text = ctk.CTkTextbox(
            parent,
            fg_color="#242424",
            text_color="#d3d3d3",  # Softer text color
            border_color="#30363d",
            border_width=1,
            wrap="word",
            corner_radius=8,
            scrollbar_button_color="#f09c3a",
            scrollbar_button_hover_color="#ff8800",
            font=("SF Mono", 12)  # Smaller font
        )
        desc_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        desc_text.insert("1.0", f"Description:\n{description}\n\n")
        desc_text.insert("end", "📝 Test Cases:\n")
        desc_text.insert("end", "─" * 40 + "\n")  # Shorter separator
        for idx, (case, ans) in enumerate(tests, 1):
            desc_text.insert("end", f"Test {idx}:\n")
            desc_text.insert("end", f"Input:  {case}\n")
            desc_text.insert("end", f"Output: {ans}\n")
            desc_text.insert("end", "─" * 20 + "\n")
        desc_text.configure(state="disabled")

        back_btn = ctk.CTkButton(
            parent,
            text="← Back to Tasks",
            command=self.destroy,
            font=("SF Pro Display", 14, "bold"),  # Smaller font
            height=36,  # Smaller button
            fg_color="#f09c3a",
            hover_color="#ff8800",
            text_color="#000000",
            corner_radius=8
        )
        back_btn.pack(fill="x", padx=10, pady=10)
        back_btn.bind("<Button-1>", self._animate_back_button)

    def _create_editor_panel(self, parent):
        """Create code editor panel"""
        editor_header = ctk.CTkFrame(parent, fg_color="transparent", height=40)  # Smaller header
        editor_header.pack(fill="x", padx=10, pady=(10, 0))
        editor_header.pack_propagate(False)

        ctk.CTkLabel(
            editor_header,
            text="💻 Code Editor",
            font=("SF Pro Display", 16, "bold"),  # Smaller font
            text_color="#f09c3a"
        ).pack(side="left", anchor="w", pady=6)

        # Static Python label
        lang_frame = ctk.CTkFrame(editor_header, fg_color="transparent")
        lang_frame.pack(side="right", anchor="e", pady=6)

        python_label = ctk.CTkLabel(
            lang_frame,
            text="🐍 Python",
            font=("SF Pro Display", 12, "bold"),  # Smaller font
            text_color="#f09c3a",
            fg_color="#2a2a2a",
            corner_radius=6,
            width=70, height=24  # Smaller label
        )
        python_label.pack(padx=4, pady=2)

        self.code_box = ctk.CTkTextbox(
            parent,
            fg_color="#000000",
            text_color="#e6edf3",
            border_color="#30363d",
            border_width=1,
            font=("SF Mono", 12),  # Smaller font
            corner_radius=8,
            wrap="none",
            scrollbar_button_color="#f09c3a",
            scrollbar_button_hover_color="#ff8800"
        )
        self.code_box.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        placeholder = """# Write your solution here
import sys


def main():
    '''Entry point for your script.'''
    # Access command line arguments via ``sys.argv[1:]``
    # Example: print(max(map(int, sys.argv[1:])))
    pass


if __name__ == "__main__":
    main()
"""
        self.code_box.insert("1.0", placeholder)

        self._create_button_panel(parent)

    def _create_button_panel(self, parent):
        """Create action buttons panel"""
        button_frame = ctk.CTkFrame(
            parent,
            fg_color="#2a2a2a",
            corner_radius=8,
            border_width=1,
            border_color="#444444",
            height=60  # Smaller panel
        )
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        button_frame.pack_propagate(False)

        buttons_data = [
            ("▶ Run", "#f09c3a", "#ff8800", self._run_code),
            ("📤 Submit", "#f09c3a", "#ff8800", self._submit_code),
            ("📁 Upload", "#f09c3a", "#ff8800", self._upload_archive)
        ]

        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(expand=True, fill="both", padx=8, pady=8)

        for text, color, hover_color, command in buttons_data:
            btn = ctk.CTkButton(
                button_container,
                text=text,
                command=command,
                font=("SF Pro Display", 12, "bold"),  # Smaller font
                height=28, width=90,  # Smaller buttons
                fg_color=color,
                hover_color=hover_color,
                text_color="#000000",
                corner_radius=8
            )
            btn.pack(side="left", padx=6, pady=4, expand=True, fill="x")
            btn.bind("<Button-1>", lambda e, b=btn: self._animate_action_button(e, b))

    def _animate_close_button(self, event):
        """Animate close button click"""
        btn = event.widget
        btn.configure(fg_color="#a93226")
        self.after(120, lambda: btn.configure(fg_color="#e74c3c"))

    def _animate_back_button(self, event):
        """Animate back button click"""
        btn = event.widget
        btn.configure(fg_color="#ff6600")
        self.after(120, lambda: btn.configure(fg_color="#f09c3a"))

    def _animate_action_button(self, event, button):
        """Animate action button click"""
        button.configure(fg_color="#ff6600")
        self.after(120, lambda: button.configure(fg_color="#f09c3a"))

    def _run_code(self):
        """Run the code using the DockerTaskRunner against stored tests."""
        from task_checker import check_solution

        code = self.code_box.get("1.0", "end")
        try:
            results, passed = check_solution(self.tests, code=code)
        except Exception as exc:
            from tkinter import messagebox
            messagebox.showerror("Execution Error", str(exc))
            return

        total = len(results)
        lines = [f"Score: {passed}/{total} tests passed"]
        for idx, r in enumerate(results, 1):
            status = "✅" if r["passed"] else "❌"
            lines.append(
                f"{status} input: '{r['input']}' expected '{r['expected']}' got '{r['output']}'"
            )

        self._show_results("Results", "\n".join(lines))

    def _submit_code(self):
        """Run tests and store the progress for this task."""
        from task_checker import check_solution
        from tkinter import messagebox

        code = self.code_box.get("1.0", "end")
        try:
            results, passed = check_solution(self.tests, code=code)
        except Exception as exc:
            messagebox.showerror("Execution Error", str(exc))
            return

        total = len(results)
        lines = [f"Score: {passed}/{total} tests passed"]
        for idx, r in enumerate(results, 1):
            status = "✅" if r["passed"] else "❌"
            lines.append(
                f"{status} input: '{r['input']}' expected '{r['expected']}' got '{r['output']}'"
            )

        if self.db and self.user_id is not None and self.task_id is not None:
            try:
                self.db.update_task_progress(self.user_id, self.task_id, passed)
            except Exception as exc:
                messagebox.showerror("DB Error", str(exc))

        self._show_results("Submission Results", "\n".join(lines))

    def _upload_archive(self):
        """Allow user to select a zip archive with solution and test it."""
        from tkinter import filedialog, messagebox
        from task_checker import check_solution

        path = filedialog.askopenfilename(
            title="Select archive",
            filetypes=[("Zip archives", "*.zip"), ("All files", "*")],
        )
        if not path:
            return

        try:
            results, passed = check_solution(self.tests, archive=path)
        except Exception as exc:
            messagebox.showerror("Execution Error", str(exc))
            return

        total = len(results)
        lines = [f"Score: {passed}/{total} tests passed"]
        for idx, r in enumerate(results, 1):
            status = "✅" if r["passed"] else "❌"
            lines.append(
                f"{status} input: '{r['input']}' expected '{r['expected']}' got '{r['output']}'"
            )

        self._show_results("Results", "\n".join(lines))

    def _show_results(self, title: str, message: str) -> None:
        """Display test results in a scrollable, copyable window."""
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("500x400")
        win.minsize(400, 300)

        text = ctk.CTkTextbox(
            win,
            wrap="none",
            fg_color="#000000",
            text_color="#e6edf3",
            scrollbar_button_color="#f09c3a",
            scrollbar_button_hover_color="#ff8800",
        )
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.insert("1.0", message)
        text.configure(state="normal")

