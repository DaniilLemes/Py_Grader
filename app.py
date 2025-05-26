import tkinter

from database import Database
from loginScene import LoginScene
from styleManager import StyleManager


class AppM(tkinter.Tk):
    def __init__(self, db: Database):
        super().__init__()
        self.title("PyGrader")
        self.geometry("1024x640")
        self.minsize(800, 520)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.style_mgr = StyleManager(self)
        LoginScene(self, db, self.style_mgr)