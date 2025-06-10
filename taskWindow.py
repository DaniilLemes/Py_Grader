import customtkinter as ctk
import tkinter as tk
from styleManager import StyleManager


class TaskWindow(ctk.CTkToplevel):
    """Simple window for solving a task."""

    def __init__(self, master: tk.Tk | tk.Toplevel, title: str,
                 description: str, style_mgr: StyleManager):
        super().__init__(master)
        self.sm = style_mgr
        self.configure(bg='#000000')
        self.geometry("900x600")
        self.resizable(False, False)
        self.title(f"Task – {title}")

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)

        # Left side with description and back button
        desc_frame = ctk.CTkFrame(
            container,
            fg_color="#1a1a1a",
            corner_radius=12,
            border_width=1,
            border_color="#f09c3a",
            width=250,
        )
        desc_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        desc_frame.rowconfigure(1, weight=1)

        ctk.CTkLabel(
            desc_frame,
            text=title,
            font=("Helvetica", 18, "bold"),
            text_color="#f09c3a",
            wraplength=220,
            justify="left",
        ).pack(padx=10, pady=(10, 5))

        desc_text = ctk.CTkTextbox(
            desc_frame,
            fg_color="#1a1a1a",
            text_color="#ffffff",
            wrap="word",
            state="disabled",
            width=220,
        )
        desc_text.pack(fill="both", expand=True, padx=10)
        desc_text.configure(state="normal")
        desc_text.insert("1.0", description)
        desc_text.configure(state="disabled")

        ctk.CTkButton(
            desc_frame,
            text="← Back",
            command=self.destroy,
            font=("Helvetica", 12, "bold"),
            height=35,
            fg_color="#f09c3a",
            hover_color="#ff8800",
            text_color="#000000",
            corner_radius=10,
        ).pack(pady=10, padx=10)

        # Right side with code editor and action buttons
        right_frame = ctk.CTkFrame(
            container,
            fg_color="#1a1a1a",
            corner_radius=12,
            border_width=1,
            border_color="#f09c3a",
        )
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        self.code_box = ctk.CTkTextbox(
            right_frame,
            fg_color="#242424",
            text_color="#ffffff",
            border_color="#f09c3a",
            border_width=1,
        )
        self.code_box.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=(10, 5))

        button_texts = ["Run", "Test", "Submit", "Upload Archive"]
        for idx, name in enumerate(button_texts):
            ctk.CTkButton(
                right_frame,
                text=name,
                state="disabled",
                font=("Helvetica", 12, "bold"),
                fg_color="#f09c3a",
                hover_color="#ff8800",
                text_color="#000000",
                corner_radius=8,
            ).grid(row=1, column=idx, padx=5, pady=10)

