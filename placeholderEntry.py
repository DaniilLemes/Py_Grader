from tkinter import ttk
import tkinter as tk



class PlaceholderEntry(ttk.Entry):
    """Entry showing placeholder text until user starts typing."""

    def __init__(self, master, placeholder: str, show: str | None = None, **kw):
        super().__init__(master, **kw)
        self.placeholder = placeholder
        self.show_char = show
        self._placeholder_on = False
        self._apply_placeholder()
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _apply_placeholder(self):
        self.insert(0, self.placeholder)
        self.config(foreground="#ffffff", show="")
        self._placeholder_on = True

    def _on_focus_in(self, _):
        if self._placeholder_on:
            self.delete(0, tk.END)
            self.config(foreground="#ffffff", show=self.show_char or "")
            self._placeholder_on = False

    def _on_focus_out(self, _):
        if not self.get():
            self._apply_placeholder()

    def value(self):
        return "" if self._placeholder_on else self.get()