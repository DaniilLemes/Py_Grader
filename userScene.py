import tkinter
from tkinter import ttk

from animatedBackground import AnimatedBackground
from database import Database
from styleManager import StyleManager

class UserScene(ttk.Frame):
    def __init__(self, master, db: Database, user_id: int, sm: StyleManager):
        super().__init__(master)
        self.db = db
        self.user_id = user_id
        self.sm = sm

        master.title("PyGrader – User")
        master.geometry("1024x640")

        # Configure grid to expand
        self.grid(sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        # Animated background layer
        AnimatedBackground(self)

        # Central content block with minimal margins and border
        block_margin = 60  # pixels from each edge to reveal background
        light_bg = "#FFE082"  # slightly lighter gold shade
        border_color = self.sm.GOLD
        self.block = tkinter.Frame(
            self,
            bg=light_bg,
            bd=0,
            highlightthickness=2,
            highlightbackground=border_color,
            highlightcolor=border_color
        )
        self.block.place(
            x=block_margin,
            y=block_margin,
            relwidth=1.0,
            relheight=1.0,
            width=-2 * block_margin,
            height=-2 * block_margin
        )

        # Prevent auto-resizing
        self.block.grid_propagate(False)
        self.block.rowconfigure(0, weight=1)
        self.block.columnconfigure(0, weight=0)
        self.block.columnconfigure(1, weight=1)

        # Left sidebar: To-do task list
        sidebar = ttk.Frame(self.block, width=200)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        # Listbox to show tasks
        self.task_list = tkinter.Listbox(sidebar, bg=self.sm.GREY_LIGHT, fg=self.sm.GREY_DARK, bd=0)
        self.task_list.pack(fill="both", expand=True, padx=10, pady=10)

        # Populate tasks from database as 'Title (expiration)'
        for task_id, title, desc, exp, rules in self.db.get_tasks_for_user(self.user_id):
            label = f"{title} ({exp or 'No due'})"
            self.task_list.insert(tkinter.END, label)

        # Placeholder area for future content
        # content_frame = ttk.Frame(self.block)
        # content_frame.grid(row=0, column=1, sticky="nsew")

        # Additional initialization if needed
        # self._populate_tasks()