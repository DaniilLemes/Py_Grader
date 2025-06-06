import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database import Database
from styleManager import StyleManager
from utils import hash_sha256
from userScene import UserScene
from adminScene import AdminScene
import random
import math

class LoginScene(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, db: Database, style_mgr: StyleManager):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.sm = style_mgr
        self.is_admin = ctk.BooleanVar(value=False)

        # Настройка окна
        self.master.configure(bg='#000000')
        self.master.geometry("800x500")
        self.master.resizable(False, False)
        self.master.title("PyGrader")

        # Создание canvas для фона и частиц
        self.canvas = tk.Canvas(self, bg='#000000', highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.grid(sticky="nsew")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        # Инициализация частиц
        self.particles = []
        self.num_particles = 25
        self._init_particles()

        # Построение UI
        self._build_ui()

        # Запуск анимаций
        self._animate_particles()

    def _init_particles(self):
        """Инициализация частиц для атмосферы"""
        for _ in range(self.num_particles):
            x = random.randint(0, 600)
            y = random.randint(0, 500)
            size = random.uniform(1, 2.5)
            speed_x = random.uniform(-0.5, 0.5)
            speed_y = random.uniform(-0.5, 0.5)
            color = random.choice(['#f09c3a', '#ffffff', '#666666'])
            opacity = random.uniform(0.3, 0.8)
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
        """Плавная анимация частиц"""
        for particle in self.particles:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']

            # Отскок от границ с небольшой случайностью
            if particle['x'] < 0 or particle['x'] > 600:
                particle['speed_x'] = -particle['speed_x'] * random.uniform(0.8, 1.2)
            if particle['y'] < 0 or particle['y'] > 500:
                particle['speed_y'] = -particle['speed_y'] * random.uniform(0.8, 1.2)

            self.canvas.coords(particle['id'],
                               particle['x'], particle['y'],
                               particle['x'] + particle['size'],
                               particle['y'] + particle['size'])
        self.master.after(30, self._animate_particles)

    def _build_ui(self):
        """Построение UI в фирменном стиле"""
        # Главный контейнер логина
        main_container = ctk.CTkFrame(
            self,
            fg_color="#000000",
            corner_radius=12,
            border_width=1,
            border_color="#f09c3a"
        )
        main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.3, relheight=0.75)
        main_container.lift()

        # Верхняя секция с логотипом
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent", height=80)
        header_frame.pack(fill="x", pady=(25, 15), padx=15)

        # Контейнер для логотипа
        logo_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_container.pack(anchor="center")

        # "Py" часть логотипа
        py_label = ctk.CTkLabel(
            logo_container,
            text="Py",
            font=("Helvetica", 28, "bold"),
            text_color="#ffffff"
        )
        py_label.pack(side="left")

        # "Grader" в оранжевом блоке
        grader_frame = ctk.CTkFrame(
            logo_container,
            fg_color="#f09c3a",
            corner_radius=8,
            width=100, height=35
        )
        grader_frame.pack(side="left", padx=(3, 0))

        grader_label = ctk.CTkLabel(
            grader_frame,
            text="Grader",
            font=("Helvetica", 28, "bold"),
            text_color="#000000"
        )
        grader_label.place(relx=0.5, rely=0.5, anchor="center")

        # Соблазнительная подпись
        subtitle = ctk.CTkLabel(
            main_container,
            text="Get ur coding satisfaction 😘",
            font=("Helvetica", 11, "italic"),
            text_color="#f09c3a"
        )
        subtitle.pack(pady=(0, 20))

        # Секция ввода данных
        input_section = ctk.CTkFrame(main_container, fg_color="transparent")
        input_section.pack(fill="x", padx=20, expand=True)

        # Поле username
        self.user_entry = ctk.CTkEntry(
            input_section,
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
        self.user_entry.pack(fill="x", pady=(0, 12))
        self.user_entry.bind("<FocusIn>", self._on_focus_in)
        self.user_entry.bind("<FocusOut>", self._on_focus_out)
        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus())

        # Поле password
        self.pass_entry = ctk.CTkEntry(
            input_section,
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
        self.pass_entry.pack(fill="x", pady=(0, 15))
        self.pass_entry.bind("<FocusIn>", self._on_focus_in)
        self.pass_entry.bind("<FocusOut>", self._on_focus_out)
        self.pass_entry.bind("<Return>", lambda e: self._login())

        # Admin режим с пикантностью
        admin_container = ctk.CTkFrame(input_section, fg_color="transparent")
        admin_container.pack(fill="x", pady=(0, 15))

        fire_emoji = ctk.CTkLabel(
            admin_container,
            text="🔥",
            font=("Arial", 14),
            text_color="#f09c3a"
        )
        fire_emoji.pack(side="left", padx=(5, 0))

        self.admin_checkbox = ctk.CTkCheckBox(
            admin_container,
            text="Admin Mode",
            variable=self.is_admin,
            font=("Helvetica", 11, "bold"),
            text_color="#ffffff",
            fg_color="#f09c3a",
            hover_color="#ff8800",
            corner_radius=6,
            border_width=1,
            border_color="#333333",
            checkbox_width=18,
            checkbox_height=18
        )
        self.admin_checkbox.pack(side="left", padx=(8, 0))

        # Главная кнопка входа
        self.login_button = ctk.CTkButton(
            main_container,
            text="🚀 LOGIN",
            command=self._login,
            font=("Helvetica", 13, "bold"),
            height=40,
            fg_color="#f09c3a",
            hover_color="#ff8800",
            border_width=0,
            corner_radius=10,
            text_color="#000000"
        )
        self.login_button.pack(fill="x", padx=20, pady=(5, 25))
        self.login_button.bind("<Button-1>", self._animate_login_button)

        # Добавляем пульсацию для кнопки
        self._pulse_login_button()

    def _on_focus_in(self, event):
        """Эффект фокуса на поле ввода"""
        try:
            event.widget.configure(border_color="#ffffff", border_width=2)
        except:
            pass  # Если не CustomTkinter виджет

    def _on_focus_out(self, event):
        """Убираем эффект фокуса"""
        try:
            event.widget.configure(border_color="#f09c3a", border_width=1)
        except:
            pass  # Если не CustomTkinter виджет

    def _animate_login_button(self, event):
        """Анимация нажатия кнопки"""
        try:
            self.login_button.configure(fg_color="#ff6600")
            self.master.after(150, lambda: self.login_button.configure(fg_color="#f09c3a"))
        except:
            pass  # Fallback если что-то пошло не так

    def _pulse_login_button(self):
        """Мягкая пульсация кнопки логина"""
        try:
            # Используем переменную для отслеживания состояния
            if not hasattr(self, '_pulse_state'):
                self._pulse_state = False

            if self._pulse_state:
                self.login_button.configure(fg_color="#f09c3a")
                self._pulse_state = False
            else:
                self.login_button.configure(fg_color="#ff8800")
                self._pulse_state = True
        except:
            pass

        self.master.after(2000, self._pulse_login_button)

    def _login(self):
        """Обработка входа в систему"""
        name = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()

        if not name or not pwd:
            self._show_error("Missing Input", "Username and password required 💔")
            return

        user_id = self.db.get_user_id(name)
        if user_id is None:
            self._show_error("Login Failed", f"No user named '{name}' found 😢")
            return

        if self.db.get_password(user_id) != hash_sha256(pwd):
            self._show_error("Login Failed", "Invalid password 🚫")
            return

        # Успешный вход
        self._show_success("Welcome!", f"Hey {name}! Ready to grade? 😎")

        self.master.withdraw()
        if self.is_admin.get():
            AdminScene(tk.Toplevel(self.master), self.db, user_id, self.sm)
        else:
            UserScene(tk.Toplevel(self.master), self.db, user_id, self.sm)

    def _show_error(self, title, message):
        """Стильное отображение ошибок"""
        messagebox.showerror(title, message)

    def _show_success(self, title, message):
        """Стильное отображение успеха"""
        messagebox.showinfo(title, message)
