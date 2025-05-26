from tkinter import ttk, messagebox
import tkinter as tk

from adminScene import AdminScene
from animatedBackground import AnimatedBackground
from database import Database
from utils import hash_sha256
from placeholderEntry import PlaceholderEntry
from styleManager import StyleManager
from userScene import UserScene


class LoginScene(ttk.Frame):
    """Combined user/admin login in a single light-gray bordered block with animated background."""

    def __init__(self, master: tk.Tk, db: Database, style_mgr: StyleManager):
        super().__init__(master)
        self.db = db
        self.sm = style_mgr
        self.is_admin = tk.BooleanVar(value=False)
        # make this frame fill the master
        self.grid(sticky="nsew")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        # Animated, particle-based background behind login block
        AnimatedBackground(self)

        # Customize 'Login.TEntry' style for dark-gray input fields
        self.sm.style.configure(
                "Login.TEntry",
                fieldbackground = "#555555",  # dark gray fill
                background = "#555555",
                foreground = "#eeeeee",  # light text
                padding = 6,
        )
        # Ensure the fill color persists in all widget states
        self.sm.style.map(
                "Login.TEntry",
                fieldbackground = [
                    ("!disabled", "#555555"),
                    ("focus", "#555555"),
                    ("active", "#555555"),
                ],
        )

        # Container frame for login elements, centered
        container = tk.Frame(
                self,
                bg = "#222222",
                padx = 30,
                pady = 30,
                bd = 1,
                highlightthickness = 1,
                highlightbackground = "#444444",
        )
        container.place(relx = 0.5, rely = 0.5, anchor = "center")

        # ----------------------------------------------------------------
        # Badge helper: draw "Grader" into an orange rounded rectangle
        # ----------------------------------------------------------------
        from PIL import Image, ImageDraw, ImageFont, ImageTk

        def make_badge(text, font_path, font_size, fg, bg, radius=8, padding=(12, 4)):
            # Try to load a TrueType font; fallback to default if that fails
            try:
                font = ImageFont.truetype(font_path, font_size)
            except Exception:
                font = ImageFont.load_default()

            # Measure text via textbbox
            dummy = Image.new("RGBA", (1, 1))
            drawer = ImageDraw.Draw(dummy)
            x0, y0, x1, y1 = drawer.textbbox((0, 0), text, font = font)
            text_w, text_h = x1 - x0, y1 - y0

            pad_x, pad_y = padding
            img_w, img_h = text_w + pad_x * 2, text_h + pad_y * 2

            # Create the badge image
            badge_img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(badge_img)
            draw.rounded_rectangle(
                    [(0, 0), (img_w, img_h)],
                    radius = radius,
                    fill = bg
            )
            draw.text((pad_x, pad_y), text, font = font, fill = fg)
            return badge_img

        # ----------------------------------------------------------------
        # Split "PyGrader" into "Py" + badge("Grader")
        # ----------------------------------------------------------------
        title_frame = tk.Frame(container, bg = "#222222")
        title_frame.pack(pady = (0, 20))

        # "Py" label
        title_py = tk.Label(
                title_frame,
                text = "Py",
                font = (self.sm.FONT[0], 16, "bold"),
                fg = StyleManager.GOLD,
                bg = "#222222",
        )
        title_py.pack(side = "left")

        # "Grader" badge
        badge_img = make_badge(
                text = "Grader",
                font_path = self.sm.FONT[0],  # or pass a full .ttf path here
                font_size = 16,
                fg = "#333333",  # dark gray text
                bg = "#FFA500",  # orange fill
                radius = 4,
                padding = (12, 8),
        )
        badge_photo = ImageTk.PhotoImage(badge_img)
        title_grader = tk.Label(
                title_frame,
                image = badge_photo,
                bg = "#222222",
                bd = 0,
        )
        title_grader.image = badge_photo  # keep a reference to avoid GC
        title_grader.pack(side = "left", padx = (5, 0))

        # ----------------------------------------------------------------
        # Login form widgets
        # ----------------------------------------------------------------
        self.user_entry = PlaceholderEntry(
                container,
                "Username",
                style = "Login.TEntry"
        )
        self.user_entry.pack(fill = "x", pady = 5)

        self.pass_entry = PlaceholderEntry(
                container,
                "Password",
                show = "*",
                style = "Login.TEntry"
        )
        self.pass_entry.pack(fill = "x", pady = 5)

        admin_chk = ttk.Checkbutton(
                container,
                text = "Admin mode",
                variable = self.is_admin,
                style = "TCheckbutton"
        )
        admin_chk.pack(pady = 10)

        login_btn = ttk.Button(
                container,
                text = "Login",
                style = "Accent.TButton",
                command = self._login
        )
        login_btn.pack(fill = "x", pady = (10, 0))

    def _login(self):
        name = self.user_entry.value()
        pwd = self.pass_entry.value()
        if not (name and pwd):
            messagebox.showwarning("Missing fields", "Username and password required.")
            return
        user_id = self.db.get_user_id(name)
        if user_id is None:
            messagebox.showerror("Login failed", f"No user named '{name}'.")
            return
        if self.db.get_password(user_id) != hash_sha256(pwd):
            messagebox.showerror("Login failed", "Incorrect password.")
            return
        self.master.withdraw()
        if self.is_admin.get():
            AdminScene(tk.Toplevel(self.master), self.db, user_id, self.sm)
        else:
            UserScene(tk.Toplevel(self.master), self.db, user_id, self.sm)