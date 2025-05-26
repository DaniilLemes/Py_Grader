import random
import tkinter as tk
from particle import Particle



class AnimatedBackground(tk.Canvas):
    """Full-window canvas that animates a bunch of Particles."""
    def __init__(self, master: tk.Tk | tk.Toplevel, num_particles: int = 50):
        super().__init__(master, highlightthickness=0)
        # sit full-window
        self.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)
        # send the canvas window behind all its sibling widgets
        master.lower(self)

        master.update_idletasks()  # ensure width/height are known
        self.particles: list[Particle] = []
        w, h = self.winfo_width(), self.winfo_height()
        for _ in range(num_particles):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            self.particles.append(Particle(self, x, y))
        self.animate()

    def animate(self):
        for p in self.particles:
            p.move()
        # roughly 30fps
        self.after(33, self.animate)