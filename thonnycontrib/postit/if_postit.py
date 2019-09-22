import tkinter as tk

from .postit import Postit
from .common import if_statement


class IfPostit(Postit):
    def __init__(self, master):
        super().__init__(master)

        self.update()

    def update(self):   # update both code and code display
        t = repr(if_statement)
        t_indented = t.replace('\n', '\n    ')

        self.set_code(t)
        self.set_code_display(t_indented)