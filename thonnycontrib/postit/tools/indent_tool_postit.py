import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup

class IndentToolPostMixin:
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
            editor_text.indent_region()

        elif pressing and selecting:
            editor_text.indent_region()

        elif dragging and not hovering:
            if editor_text.tag_ranges(tk.SEL):
                editor_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            editor_text.indent_region()
            

        elif dragging and hovering:
            editor_text.indent_region()

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
            pass

class DedentToolPostMixin:
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
            editor_text.dedent_region()

        elif pressing and selecting:
            editor_text.dedent_region()

        elif dragging and not hovering:
            if editor_text.tag_ranges(tk.SEL):
                editor_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            editor_text.dedent_region()
            

        elif dragging and hovering:
            editor_text.dedent_region()

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
            pass



class IndentToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 IndentToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'indent')
        self.code_init()
        self.post_init()
        #self.popup_init()

class DedentToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 DedentToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'dedent')
        self.code_init()
        self.post_init()
        #self.popup_init()

