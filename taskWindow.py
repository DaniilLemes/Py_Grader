import customtkinter as ctk
import tkinter as tk
from styleManager import StyleManager
import random

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
    ):
        super().__init__(master)
        self.sm = style_mgr
        self.configure(fg_color="#000000")
        self.geometry("900x600")
        self.resizable(False, False)
        self.title(f"PyGrader – {title}")

        # Make window modal and center it
        self.transient(master)
        self.grab_set()
        self._center_window()

        # Canvas for animated particle background
        self.canvas = tk.Canvas(self, bg='#000000', highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Initialize particles
        self.particles = []
        self.num_particles = 50
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
            x = random.randint(0, 900)
            y = random.randint(0, 600)
            size = random.uniform(1.5, 4)
            speed_x = random.uniform(-0.4, 0.4)
            speed_y = random.uniform(-0.4, 0.4)
            color = random.choice(['#f09c3a', '#ffffff', '#666666'])
            # Use valid Tkinter stipple patterns
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

                # Bounce with subtle randomness
                if particle['x'] < 0 or particle['x'] > 900:
                    particle['speed_x'] = -particle['speed_x'] * random.uniform(0.85, 1.15)
                if particle['y'] < 0 or particle['y'] > 600:
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
            print(f"Animation error: {e}")  # Log errors gracefully

    def _create_header(self, parent, title):
        """Create modern header with logo and title"""
        header_frame = ctk.CTkFrame(
            parent,
            fg_color="#1e1e1e",
            corner_radius=16,
            border_width=1,
            border_color="#f09c3a",
            height=70
        )
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)

        # Left side - Logo
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="y", padx=20)

        logo_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        logo_container.pack(anchor="center", expand=True)

        ctk.CTkLabel(
            logo_container,
            text="Py",
            font=("SF Pro Display", 28, "bold"),
            text_color="#ffffff"
        ).pack(side="left")

        grader_frame = ctk.CTkFrame(
            logo_container,
            fg_color="#f09c3a",
            corner_radius=10,
            width=95, height=36
        )
        grader_frame.pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            grader_frame,
            text="Grader",
            font=("SF Pro Display", 28, "bold"),
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Center - Task title
        center_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        center_frame.pack(side="left", fill="both", expand=True, padx=25)

        title_label = ctk.CTkLabel(
            center_frame,
            text=f"📝 {title}",
            font=("SF Pro Display", 24, "bold"),
            text_color="#f09c3a"
        )
        title_label.pack(anchor="center", expand=True)

        # Right side - Close button (менее закругленная и меньше)
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="y", padx=20)

        close_btn = ctk.CTkButton(
            right_frame,
            text="✕",
            command=self.destroy,
            font=("SF Pro Display", 16, "bold"),
            width=32, height=32,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            text_color="#ffffff",
            corner_radius=6  # Менее закругленная
        )
        close_btn.pack(anchor="center", expand=True)
        close_btn.bind("<Button-1>", self._animate_close_button)

    def _create_content(self, parent, title, description, expiration, tests):
        """Create main content area with task description and code editor"""
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Left panel - Task description
        left_panel = ctk.CTkFrame(
            content_frame,
            fg_color="#1e1e1e",
            corner_radius=16,
            border_width=1,
            border_color="#333333",
            width=340
        )
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        left_panel.pack_propagate(False)

        self._create_description_panel(left_panel, description, expiration, tests)

        # Right panel - Code editor
        right_panel = ctk.CTkFrame(
            content_frame,
            fg_color="#1e1e1e",
            corner_radius=16,
            border_width=1,
            border_color="#333333"
        )
        right_panel.pack(side="right", fill="both", expand=True)

        self._create_editor_panel(right_panel)

    def _create_description_panel(self, parent, description, expiration, tests):
        """Create task description panel"""
        desc_header = ctk.CTkFrame(parent, fg_color="transparent", height=55)
        desc_header.pack(fill="x", padx=15, pady=(15, 0))
        desc_header.pack_propagate(False)

        ctk.CTkLabel(
            desc_header,
            text="📋 Task Details",
            font=("SF Pro Display", 22, "bold"),
            text_color="#f09c3a"
        ).pack(anchor="w", pady=10)

        if expiration:
            exp_frame = ctk.CTkFrame(
                parent,
                fg_color="#2a2a2a",
                corner_radius=12,
                border_width=1,
                border_color="#444444"
            )
            exp_frame.pack(fill="x", padx=15, pady=(0, 15))

            ctk.CTkLabel(
                exp_frame,
                text=f"⏱️ Deadline: {expiration}",
                font=("SF Pro Display", 14, "normal"),
                text_color="#ffffff"
            ).pack(pady=8)

        desc_text = ctk.CTkTextbox(
            parent,
            fg_color="#242424",
            text_color="#e0e0e0",
            border_color="#444444",
            border_width=1,
            wrap="word",
            font=("SF Mono", 12),
            corner_radius=12,
            scrollbar_button_color="#f09c3a",
            scrollbar_button_hover_color="#ff8800"
        )
        desc_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        desc_text.insert("1.0", f"Description:\n{description}\n\n")
        desc_text.insert("end", "📝 Test Cases:\n")
        desc_text.insert("end", "─" * 50 + "\n")

        for idx, (case, ans) in enumerate(tests, 1):
            desc_text.insert("end", f"Test {idx}:\n")
            desc_text.insert("end", f"Input:  {case}\n")
            desc_text.insert("end", f"Output: {ans}\n")
            desc_text.insert("end", "─" * 25 + "\n")

        desc_text.configure(state="disabled")

        back_btn = ctk.CTkButton(
            parent,
            text="← Back to Tasks",
            command=self.destroy,
            font=("SF Pro Display", 16, "bold"),
            height=45,
            fg_color="#f09c3a",
            hover_color="#ff8800",
            text_color="#000000",
            corner_radius=12
        )
        back_btn.pack(fill="x", padx=15, pady=15)
        back_btn.bind("<Button-1>", self._animate_back_button)

    def _create_editor_panel(self, parent):
        """Create code editor panel"""
        editor_header = ctk.CTkFrame(parent, fg_color="transparent", height=55)
        editor_header.pack(fill="x", padx=15, pady=(15, 0))
        editor_header.pack_propagate(False)

        ctk.CTkLabel(
            editor_header,
            text="💻 Code Editor",
            font=("SF Pro Display", 22, "bold"),
            text_color="#f09c3a"
        ).pack(side="left", anchor="w", pady=10)

        # Упрощенный селектор языка (только Python)
        lang_frame = ctk.CTkFrame(editor_header, fg_color="transparent")
        lang_frame.pack(side="right", anchor="e", pady=10)

        python_label = ctk.CTkLabel(
            lang_frame,
            text="🐍 Python",
            font=("SF Pro Display", 14, "bold"),
            text_color="#f09c3a",
            fg_color="#2a2a2a",
            corner_radius=8,
            width=80,
            height=28
        )
        python_label.pack(padx=5, pady=2)

        self.code_box = ctk.CTkTextbox(
            parent,
            fg_color="#0d1117",
            text_color="#e6edf3",
            border_color="#30363d",
            border_width=1,
            font=("SF Mono", 13),
            corner_radius=12,
            wrap="none",
            scrollbar_button_color="#f09c3a",
            scrollbar_button_hover_color="#ff8800"
        )
        self.code_box.pack(fill="both", expand=True, padx=15, pady=(15, 15))

        placeholder = """# Write your solution here
def solution():
    \"\"\"
    Implement your solution here.
    \"\"\"
    # Your code goes here
    pass

# Example usage:
# result = solution()
# print(result)"""
        self.code_box.insert("1.0", placeholder)

        self._create_button_panel(parent)

    def _create_button_panel(self, parent):
        """Create action buttons panel"""
        button_frame = ctk.CTkFrame(
            parent,
            fg_color="#2a2a2a",
            corner_radius=12,
            border_width=1,
            border_color="#444444",
            height=75
        )
        button_frame.pack(fill="x", padx=15, pady=(0, 15))
        button_frame.pack_propagate(False)

        buttons_data = [
            ("▶ Run", "#f09c3a", "#ff8800", self._run_code),
            ("🧪 Test", "#f09c3a", "#ff8800", self._test_code),
            ("📤 Submit", "#f09c3a", "#ff8800", self._submit_code),
            ("📁 Upload", "#f09c3a", "#ff8800", self._upload_archive)
        ]

        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(expand=True, fill="both", padx=10, pady=10)

        for i, (text, color, hover_color, command) in enumerate(buttons_data):
            btn = ctk.CTkButton(
                button_container,
                text=text,
                command=command,
                font=("SF Pro Display", 14, "bold"),
                height=32,
                width=100,
                fg_color=color,
                hover_color=hover_color,
                text_color="#000000",
                corner_radius=10
            )
            btn.pack(side="left", padx=8, pady=5, expand=True, fill="x")
            btn.bind("<Button-1>", lambda e, b=btn: self._animate_action_button(e, b))


    def _animate_close_button(self, event):
        """Animate close button click"""
        btn = event.widget
        btn.configure(fg_color="#a93226")
        self.after(150, lambda: btn.configure(fg_color="#e74c3c"))

    def _animate_back_button(self, event):
        """Animate back button click"""
        btn = event.widget
        btn.configure(fg_color="#ff6600")
        self.after(150, lambda: btn.configure(fg_color="#f09c3a"))

    def _animate_action_button(self, event, button):
        """Animate action button click"""
        original_color = button.cget("fg_color")
        button.configure(fg_color="#444444")
        self.after(150, lambda: button.configure(fg_color=original_color))

    def _run_code(self):
        """Run the code (placeholder)"""
        print("Running code...")

    def _test_code(self):
        """Test the code (placeholder)"""
        print("Testing code...")

    def _submit_code(self):
        """Submit the code (placeholder)"""
        print("Submitting code...")

    def _upload_archive(self):
        """Upload archive (placeholder)"""
        print("Uploading archive...")
