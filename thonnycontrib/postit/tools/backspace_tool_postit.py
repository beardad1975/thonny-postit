import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup


class BackspaceToolPostMixin:
    def post_init(self):
        self.drag_window = None
        self.drag_button = None
        self.drag_hover_selection = False
        self.hover_text_backup = ''
        #self.mouse_dragging = False
        # drag and press event
        #self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<Button-1>", self.on_mouse_release)
        #self.postit_button.config(cursor='arrow')

    def insert_into_editor(self, editor_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        if pressing and not selecting:
            editor_text.event_generate("<BackSpace>")

        elif pressing and selecting:
            editor_text.event_generate("<BackSpace>")

        elif dragging and not hovering:
            if editor_text.tag_ranges(tk.SEL):
                editor_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            editor_text.delete(tk.INSERT + '-1c')

        elif dragging and hovering:
            editor_text.event_generate("<BackSpace>")

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        if pressing and not selecting:
            shell_text.event_generate("<BackSpace>")

        elif pressing and selecting:
            if shell_text.compare(tk.SEL_LAST, '>', 'input_start'):
                if shell_text.compare(tk.SEL_FIRST, '>=', 'input_start'):
                    shell_text.event_generate("<BackSpace>")
                else:
                    shell_text.delete('input_start', tk.SEL_LAST)
                    shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            
        elif dragging and not hovering:
            if shell_text.tag_ranges(tk.SEL):
                shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            shell_text.delete(tk.INSERT + '-1c')

        elif dragging and hovering:
            shell_text.event_generate("<BackSpace>")

class BackspaceToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 BackspaceToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'backspace')
        self.code_init()
        self.post_init()
        #self.popup_init()