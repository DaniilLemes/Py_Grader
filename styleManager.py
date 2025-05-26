
import tkinter
from tkinter import ttk

# Attempt to import ttkbootstrap, fallback to stock ttk
try:
    import ttkbootstrap as ttkb
    _THEME_LIB = 'ttkbootstrap'
except ModuleNotFoundError:
    ttkb = None  # type: ignore
    _THEME_LIB = 'ttk'

class StyleManager:
    """Singleton-like helper that wires the Binance palette into ttk/ttkbootstrap."""

    GOLD = "#f0b90b"
    BLACK = "#0c0e12"
    GREY_DARK = "#1a1c20"
    GREY_LIGHT = "#2a2d32"

    FONT = ("Inter", 11)

    def __init__(self, root: tkinter.Tk | tkinter.Toplevel):
        self.root = root
        if ttkb:
            self.style = ttkb.Style("darkly")
        else:
            self.style = ttk.Style()
            self.style.theme_use("clam")
        self._configure_base()


    def _configure_base(self):
        """Create base widget styles."""
        s = self.style
        bg = self.BLACK
        fg = "#ffffff"
        accent = self.GOLD

        self.root.configure(bg=bg)

        s.configure("TFrame", background=bg)
        s.configure(
            "TLabel", background=bg, foreground=fg, font=self.FONT, padding=2
        )
        s.configure(
            "Header.TLabel", font=(self.FONT[0], 16, "bold"), foreground=accent
        )
        s.configure(
            "Accent.TButton",
            background=accent,
            foreground=bg,
            font=self.FONT,
            relief="flat",
            padding=8,
        )
        s.map(
            "Accent.TButton",
            background=[("active", "#d9a509"), ("disabled", "#7a6432")],
        )


        s.configure(
                    "TEntry",
                    fieldbackground = "#444444",  # dark gray fill
                    background = "#444444",
                    foreground = "#ffffff",  # white text by default
                    padding = 6,
            )
            # make sure the Entry doesn’t switch back to white on focus:
        s.map(
                    "TEntry",
                    fieldbackground = [
                        ("!disabled", "#444444"),
                        ("focus", "#444444"),
                        ("active", "#444444"),
                    ],
            )
        self.root.option_add("*Listbox.background", self.GREY_DARK)
        self.root.option_add("*Listbox.foreground", fg)
        self.root.option_add("*Listbox.selectBackground", accent)
        self.root.option_add("*Listbox.selectForeground", bg)

    def toggle_theme(self):
        """Switch between dark and light themes (ttkbootstrap only)."""
        if not ttkb:
            return
        current = self.style.theme.name  # type: ignore
        self.style.theme_use("flatly" if current == "darkly" else "darkly")