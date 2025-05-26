import math
import random
import tkinter as tk

from styleManager import StyleManager


class Particle:
    """A single moving dot on the canvas."""
    def __init__(self, canvas: tk.Canvas, x: float, y: float, size: int = 4):
        self.canvas = canvas
        self.size = size
        # random direction & speed
        angle = random.uniform(0, 2 * 3.1416)
        speed = random.uniform(0.5, 2.0)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        # draw as oval
        self.id = canvas.create_oval(
            x, y, x + size, y + size,
            fill=StyleManager.GOLD, outline=""
        )

    def move(self):
        # move and wrap around edges
        x1, y1, x2, y2 = self.canvas.coords(self.id)
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        # update position
        self.canvas.move(self.id, self.vx, self.vy)
        # get new coords
        x1, y1, x2, y2 = self.canvas.coords(self.id)
        # wrap X
        if x2 < 0:
            self.canvas.move(self.id, w + self.size, 0)
        elif x1 > w:
            self.canvas.move(self.id, -(w + self.size), 0)
        # wrap Y
        if y2 < 0:
            self.canvas.move(self.id, 0, h + self.size)
        elif y1 > h:
            self.canvas.move(self.id, 0, -(h + self.size))
