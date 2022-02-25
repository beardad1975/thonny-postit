import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup


class UndoToolPostMixin:
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
        
        editor_text.edit_undo()

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        if shell_text.compare('input_start', '==','end-1c'):
            # empty line
            shell_text.event_generate("<Up>")
        else: # not empty line
            shell_text.edit_undo()

class RedoToolPostMixin:
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
        
        editor_text.edit_redo()

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        shell_text.edit_redo()


class UndoToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 UndoToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'undo')
        self.code_init()
        self.post_init()
        #self.popup_init()

class RedoToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 RedoToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'redo')
        self.code_init()
        self.post_init()
        #self.popup_init()